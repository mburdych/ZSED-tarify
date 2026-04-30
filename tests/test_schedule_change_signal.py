"""Tests for coordinator schedule-change signaling contract."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types
from unittest.mock import AsyncMock

import pytest


def _load_coordinator_module():
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
    spec = spec_from_file_location("custom_components.zse_hdo.coordinator", coordinator_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _schedule(start: str, end: str):
    return {
        "hdo_number": 145,
        "workday": [{"start": start, "end": end, "tariff": "low"}],
        "weekend": [],
        "rate_type": "D3",
    }


@pytest.mark.asyncio
async def test_schedule_changed_flag_only_when_payload_differs():
    module = _load_coordinator_module()
    parser = types.SimpleNamespace(
        get_schedule=AsyncMock(
            side_effect=[
                _schedule("12:00", "13:00"),
                _schedule("12:00", "13:00"),
                _schedule("11:00", "13:00"),
            ]
        )
    )
    coordinator = module.ZSEHDOCoordinator(object(), parser, 145, "5min")
    t0 = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module.dt_util, "now", lambda: t0)
        first = await coordinator._async_update_data()
        mp.setattr(module.dt_util, "now", lambda: t0 + timedelta(minutes=10))
        second = await coordinator._async_update_data()
        mp.setattr(module.dt_util, "now", lambda: t0 + timedelta(minutes=20))
        third = await coordinator._async_update_data()

    assert first["schedule_changed"] is False
    assert first["schedule_change_at"] is None
    assert second["schedule_changed"] is False
    assert second["schedule_change_at"] is None
    assert third["schedule_changed"] is True
    assert third["schedule_change_at"] == (t0 + timedelta(minutes=20)).isoformat()
