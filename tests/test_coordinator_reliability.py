"""Coordinator reliability contract tests (retry/backoff + stale metadata)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types
from unittest.mock import AsyncMock

import pytest


def _load_coordinator_module():
    """Load coordinator module with lightweight HA test doubles."""
    root = Path(__file__).parents[1]
    package_dir = root / "custom_components" / "zse_hdo"

    custom_components_pkg = types.ModuleType("custom_components")
    custom_components_pkg.__path__ = [str(root / "custom_components")]
    sys.modules["custom_components"] = custom_components_pkg

    zse_pkg = types.ModuleType("custom_components.zse_hdo")
    zse_pkg.__path__ = [str(package_dir)]
    sys.modules["custom_components.zse_hdo"] = zse_pkg

    class _FakeCoordinator:
        def __init__(self, hass, logger, name, update_interval=None):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval

        async def async_request_refresh(self):
            return None

    class _FakeUpdateFailed(Exception):
        def __init__(self, message, retry_after=None):
            super().__init__(message)
            self.retry_after = retry_after

    homeassistant_pkg = types.ModuleType("homeassistant")
    homeassistant_pkg.__path__ = []
    sys.modules["homeassistant"] = homeassistant_pkg

    ha_core = types.ModuleType("homeassistant.core")
    ha_core.HomeAssistant = object
    sys.modules["homeassistant.core"] = ha_core

    ha_helpers = types.ModuleType("homeassistant.helpers")
    ha_helpers.__path__ = []
    sys.modules["homeassistant.helpers"] = ha_helpers

    ha_update = types.ModuleType("homeassistant.helpers.update_coordinator")
    ha_update.DataUpdateCoordinator = _FakeCoordinator
    ha_update.UpdateFailed = _FakeUpdateFailed
    sys.modules["homeassistant.helpers.update_coordinator"] = ha_update

    ha_event = types.ModuleType("homeassistant.helpers.event")
    ha_event.async_track_point_in_time = lambda hass, callback, when: (lambda: None)
    sys.modules["homeassistant.helpers.event"] = ha_event

    ha_util = types.ModuleType("homeassistant.util")
    ha_util.__path__ = []
    sys.modules["homeassistant.util"] = ha_util

    ha_dt = types.ModuleType("homeassistant.util.dt")
    ha_dt.now = lambda: datetime.now(timezone.utc)
    sys.modules["homeassistant.util.dt"] = ha_dt

    parser_stub = types.ModuleType("custom_components.zse_hdo.parser")
    parser_stub.ZSEHDOFetchError = type("ZSEHDOFetchError", (Exception,), {})
    parser_stub.ZSEHDOParseError = type("ZSEHDOParseError", (Exception,), {})
    parser_stub.ZSEHDOTariffLogicError = type("ZSEHDOTariffLogicError", (Exception,), {})
    parser_stub.ZSEHDOLiveParser = object
    sys.modules["custom_components.zse_hdo.parser"] = parser_stub

    const_path = package_dir / "const.py"
    const_spec = spec_from_file_location("custom_components.zse_hdo.const", const_path)
    const_module = module_from_spec(const_spec)
    assert const_spec and const_spec.loader
    const_spec.loader.exec_module(const_module)
    sys.modules["custom_components.zse_hdo.const"] = const_module

    coordinator_path = package_dir / "coordinator.py"
    spec = spec_from_file_location(
        "custom_components.zse_hdo.coordinator", coordinator_path
    )
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_repeated_failures_increase_backoff_and_failure_counters():
    module = _load_coordinator_module()
    parser = types.SimpleNamespace(get_schedule=AsyncMock(side_effect=RuntimeError("boom")))
    coordinator = module.ZSEHDOCoordinator(object(), parser, 145, "5min")

    start = datetime(2026, 4, 29, 12, 0, tzinfo=timezone.utc)
    coordinator._last_known_data = {
        "hdo_number": 145,
        "workday": [],
        "weekend": [],
        "rate_type": "household",
    }

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            module.dt_util,
            "now",
            lambda: start + timedelta(minutes=10),
        )
        first = await coordinator._async_update_data()
        mp.setattr(
            module.dt_util,
            "now",
            lambda: start + timedelta(minutes=20),
        )
        second = await coordinator._async_update_data()

    assert first["consecutive_failures"] == 1
    assert second["consecutive_failures"] == 2
    assert first["is_stale"] is True
    assert second["is_stale"] is True
    assert first["next_retry_at"] is not None
    assert second["next_retry_at"] is not None

    first_retry = datetime.fromisoformat(first["next_retry_at"])
    second_retry = datetime.fromisoformat(second["next_retry_at"])
    second_now = start + timedelta(minutes=20)
    assert (first_retry - (start + timedelta(minutes=10))).total_seconds() > 0
    assert (second_retry - second_now).total_seconds() > 0
    assert (second_retry - second_now).total_seconds() <= 21600


@pytest.mark.asyncio
async def test_cached_fallback_explicitly_marks_payload_stale():
    module = _load_coordinator_module()
    parser = types.SimpleNamespace(get_schedule=AsyncMock())
    coordinator = module.ZSEHDOCoordinator(object(), parser, 145, "5min")
    t0 = datetime(2026, 4, 29, 10, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=35)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module.dt_util, "now", lambda: t0)
        parser.get_schedule.return_value = {
            "hdo_number": 145,
            "workday": [{"start": "01:00", "end": "02:00"}],
            "weekend": [],
            "rate_type": "household",
        }
        await coordinator._async_update_data()

    parser.get_schedule = AsyncMock(side_effect=RuntimeError("temporary outage"))

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module.dt_util, "now", lambda: t1)
        cached = await coordinator._async_update_data()

    assert cached["is_stale"] is True
    assert cached["stale_for_s"] == 2100
    assert cached["last_success_at"] == t0.isoformat()
    assert cached["last_error_at"] == t1.isoformat()
    assert cached["consecutive_failures"] == 1
    assert cached["next_retry_at"] is not None


@pytest.mark.asyncio
async def test_success_after_failure_resets_stale_and_failure_state():
    module = _load_coordinator_module()
    parser = types.SimpleNamespace(get_schedule=AsyncMock())
    coordinator = module.ZSEHDOCoordinator(object(), parser, 145, "5min")
    t0 = datetime(2026, 4, 29, 9, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=10)
    t2 = t1 + timedelta(minutes=5)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module.dt_util, "now", lambda: t0)
        parser.get_schedule.return_value = {
            "hdo_number": 145,
            "workday": [],
            "weekend": [],
            "rate_type": "household",
        }
        await coordinator._async_update_data()

    parser.get_schedule = AsyncMock(side_effect=RuntimeError("network down"))
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module.dt_util, "now", lambda: t1)
        stale = await coordinator._async_update_data()
    assert stale["is_stale"] is True
    assert stale["consecutive_failures"] == 1

    parser.get_schedule = AsyncMock(
        return_value={
            "hdo_number": 145,
            "workday": [{"start": "05:00", "end": "06:00"}],
            "weekend": [],
            "rate_type": "household",
        }
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module.dt_util, "now", lambda: t2)
        recovered = await coordinator._async_update_data()

    assert recovered["is_stale"] is False
    assert recovered["stale_for_s"] == 0
    assert recovered["consecutive_failures"] == 0
    assert recovered["last_success_at"] == t2.isoformat()
    assert recovered["last_error_at"] is None
    assert recovered["next_retry_at"] is None
