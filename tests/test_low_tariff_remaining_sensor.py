"""Tests for remaining low-tariff helper sensor."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types

import pytest


def _load_sensor_module(now_dt: datetime):
    """Load sensor module with deterministic time and lightweight HA stubs."""
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
    ha_dt.now = lambda: now_dt
    sys.modules["homeassistant.util.dt"] = ha_dt

    const_path = package_dir / "const.py"
    const_spec = spec_from_file_location("custom_components.zse_hdo.const", const_path)
    const_module = module_from_spec(const_spec)
    assert const_spec and const_spec.loader
    const_spec.loader.exec_module(const_module)
    sys.modules["custom_components.zse_hdo.const"] = const_module

    time_semantics_path = package_dir / "time_semantics.py"
    ts_spec = spec_from_file_location(
        "custom_components.zse_hdo.time_semantics", time_semantics_path
    )
    ts_module = module_from_spec(ts_spec)
    assert ts_spec and ts_spec.loader
    ts_spec.loader.exec_module(ts_module)
    sys.modules["custom_components.zse_hdo.time_semantics"] = ts_module

    sensor_path = package_dir / "sensor.py"
    sensor_spec = spec_from_file_location("custom_components.zse_hdo.sensor", sensor_path)
    sensor_module = module_from_spec(sensor_spec)
    assert sensor_spec and sensor_spec.loader
    sensor_spec.loader.exec_module(sensor_module)
    return sensor_module


def _payload(workday, weekend=None):
    return {
        "hdo_number": 145,
        "workday": workday,
        "weekend": weekend or [],
        "current_tariff": "low",
        "category": "household",
        "rate_type": "D3 Aktiv (DD3*)",
        "is_stale": False,
        "stale_for_s": 0,
        "consecutive_failures": 0,
        "last_success_at": "2026-04-30T12:00:00+02:00",
        "last_error_at": None,
        "next_retry_at": None,
    }


def _entity(now_dt: datetime, payload: dict):
    module = _load_sensor_module(now_dt)
    coordinator = types.SimpleNamespace(data=payload)
    entry = types.SimpleNamespace(entry_id="entry-1")
    return module.ZSEHDOLowRemainingSensor(coordinator, entry, 145)


def test_remaining_minutes_in_active_workday_period():
    now = datetime(2026, 4, 30, 12, 15, tzinfo=timezone.utc)
    entity = _entity(now, _payload([{"start": "12:00", "end": "13:00", "tariff": "low"}]))
    assert entity.native_value == 45
    attrs = entity.extra_state_attributes
    assert attrs["is_low_tariff_now"] is True
    assert attrs["remaining_minutes"] == 45
    assert attrs["period_end"].endswith("13:00:00+00:00")


def test_remaining_minutes_is_zero_outside_low_tariff():
    now = datetime(2026, 4, 30, 14, 30, tzinfo=timezone.utc)
    entity = _entity(now, _payload([{"start": "12:00", "end": "13:00", "tariff": "low"}]))
    assert entity.native_value == 0
    attrs = entity.extra_state_attributes
    assert attrs["is_low_tariff_now"] is False
    assert attrs["period_end"] is None


def test_midnight_crossing_period_is_handled():
    now = datetime(2026, 4, 30, 23, 50, tzinfo=timezone.utc)
    entity = _entity(now, _payload([{"start": "23:45", "end": "05:45", "tariff": "low"}]))
    assert entity.native_value == 355
    assert entity.extra_state_attributes["is_low_tariff_now"] is True


def test_weekend_schedule_branch_used():
    now = datetime(2026, 5, 2, 9, 15, tzinfo=timezone.utc)  # Saturday
    entity = _entity(
        now,
        _payload(
            [{"start": "12:00", "end": "13:00", "tariff": "low"}],
            weekend=[{"start": "09:00", "end": "10:00", "tariff": "low"}],
        ),
    )
    assert entity.native_value == 45
