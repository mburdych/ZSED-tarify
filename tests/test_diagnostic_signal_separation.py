"""Diagnostic contract tests for fetch/parse/tariff error separation."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types
from unittest.mock import AsyncMock

import pytest


def _load_coordinator_module():
    """Load coordinator with parser diagnostic exception stubs."""
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

    class _FetchError(Exception):
        pass

    class _ParseError(Exception):
        pass

    class _TariffLogicError(Exception):
        pass

    parser_stub.ZSEHDOLiveParser = object
    parser_stub.ZSEHDOFetchError = _FetchError
    parser_stub.ZSEHDOParseError = _ParseError
    parser_stub.ZSEHDOTariffLogicError = _TariffLogicError
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
    return module, parser_stub


def _load_sensor_module():
    """Load sensor module for entity attribute projection assertions."""
    root = Path(__file__).parents[1]
    package_dir = root / "custom_components" / "zse_hdo"

    custom_components_pkg = types.ModuleType("custom_components")
    custom_components_pkg.__path__ = [str(root / "custom_components")]
    sys.modules["custom_components"] = custom_components_pkg

    zse_pkg = types.ModuleType("custom_components.zse_hdo")
    zse_pkg.__path__ = [str(package_dir)]
    sys.modules["custom_components.zse_hdo"] = zse_pkg

    homeassistant_pkg = types.ModuleType("homeassistant")
    homeassistant_pkg.__path__ = []
    sys.modules["homeassistant"] = homeassistant_pkg

    ha_binary_sensor = types.ModuleType("homeassistant.components.binary_sensor")
    ha_binary_sensor.BinarySensorEntity = type("BinarySensorEntity", (), {})
    ha_binary_sensor.BinarySensorDeviceClass = types.SimpleNamespace(POWER="power")
    sys.modules["homeassistant.components.binary_sensor"] = ha_binary_sensor

    ha_sensor = types.ModuleType("homeassistant.components.sensor")
    ha_sensor.SensorEntity = type("SensorEntity", (), {})
    sys.modules["homeassistant.components.sensor"] = ha_sensor

    ha_config_entries = types.ModuleType("homeassistant.config_entries")
    ha_config_entries.ConfigEntry = object
    sys.modules["homeassistant.config_entries"] = ha_config_entries

    ha_core = types.ModuleType("homeassistant.core")
    ha_core.HomeAssistant = object
    ha_core.callback = lambda func: func
    sys.modules["homeassistant.core"] = ha_core

    ha_entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    ha_entity_platform.AddEntitiesCallback = object
    sys.modules["homeassistant.helpers.entity_platform"] = ha_entity_platform

    class _FakeCoordinatorEntity:
        def __init__(self, coordinator):
            self.coordinator = coordinator

    ha_update = types.ModuleType("homeassistant.helpers.update_coordinator")
    ha_update.CoordinatorEntity = _FakeCoordinatorEntity
    sys.modules["homeassistant.helpers.update_coordinator"] = ha_update

    ha_util = types.ModuleType("homeassistant.util")
    ha_util.__path__ = []
    sys.modules["homeassistant.util"] = ha_util

    ha_dt = types.ModuleType("homeassistant.util.dt")
    ha_dt.now = lambda: datetime(2026, 4, 29, 12, 0, tzinfo=timezone.utc)
    sys.modules["homeassistant.util.dt"] = ha_dt

    const_path = package_dir / "const.py"
    const_spec = spec_from_file_location("custom_components.zse_hdo.const", const_path)
    const_module = module_from_spec(const_spec)
    assert const_spec and const_spec.loader
    const_spec.loader.exec_module(const_module)
    sys.modules["custom_components.zse_hdo.const"] = const_module

    time_semantics = types.ModuleType("custom_components.zse_hdo.time_semantics")
    time_semantics.calculate_next_switch = lambda data, now: {
        "time": "14:00",
        "to_tariff": "low",
        "datetime": datetime(2026, 4, 29, 14, 0, tzinfo=timezone.utc),
    }
    time_semantics.get_periods_for_datetime = (
        lambda data, now: data.get("workday", []) if data else []
    )
    time_semantics.is_low_tariff = lambda data, now: bool(data.get("workday"))
    sys.modules["custom_components.zse_hdo.time_semantics"] = time_semantics

    sensor_path = package_dir / "sensor.py"
    sensor_spec = spec_from_file_location("custom_components.zse_hdo.sensor", sensor_path)
    sensor_module = module_from_spec(sensor_spec)
    assert sensor_spec and sensor_spec.loader
    sensor_spec.loader.exec_module(sensor_module)
    return sensor_module


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error_cls_name", "expected_source"),
    [
        ("ZSEHDOFetchError", "fetch"),
        ("ZSEHDOParseError", "parse"),
        ("ZSEHDOTariffLogicError", "tariff_logic"),
    ],
)
async def test_error_source_classification_on_cached_fallback(error_cls_name, expected_source):
    module, parser_stub = _load_coordinator_module()
    err_cls = getattr(parser_stub, error_cls_name)
    parser = types.SimpleNamespace(get_schedule=AsyncMock(side_effect=err_cls("boom")))
    coordinator = module.ZSEHDOCoordinator(object(), parser, 145, "5min")
    now = datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc)
    coordinator._last_known_data = {
        "hdo_number": 145,
        "workday": [],
        "weekend": [],
        "rate_type": "D3",
    }

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module.dt_util, "now", lambda: now)
        payload = await coordinator._async_update_data()

    assert payload["diagnostic_error_source"] == expected_source
    assert payload["diagnostic_error_code"] is not None
    assert payload["diagnostic_error_at"] == now.isoformat()


def test_sensor_entities_project_diagnostic_markers():
    sensor_module = _load_sensor_module()
    payload = {
        "workday": [{"start": "10:00", "end": "11:00", "tariff": "low"}],
        "weekend": [],
        "category": "household",
        "rate_type": "D3",
        "is_stale": True,
        "stale_for_s": 60,
        "consecutive_failures": 1,
        "last_success_at": "2026-04-30T11:58:00+00:00",
        "last_error_at": "2026-04-30T11:59:00+00:00",
        "next_retry_at": "2026-04-30T12:00:30+00:00",
        "diagnostic_error_source": "parse",
        "diagnostic_error_code": "PARSE_ERROR",
        "diagnostic_error_at": "2026-04-30T11:59:00+00:00",
    }
    coordinator = types.SimpleNamespace(data=payload)
    entry = types.SimpleNamespace(entry_id="entry-1")
    entities = [
        sensor_module.ZSEHDOTariffSensor(coordinator, entry, 145),
        sensor_module.ZSEHDONextSwitchSensor(coordinator, entry, 145),
        sensor_module.ZSEHDOTodayScheduleSensor(coordinator, entry, 145),
    ]

    for entity in entities:
        attrs = entity.extra_state_attributes
        assert attrs["diagnostic_error_source"] == "parse"
        assert attrs["diagnostic_error_code"] == "PARSE_ERROR"
        assert attrs["diagnostic_error_at"] == "2026-04-30T11:59:00+00:00"
