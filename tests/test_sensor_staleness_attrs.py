"""Contract tests for staleness metadata on existing sensor entities."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types

import pytest


def _load_sensor_module():
    """Load sensor module with lightweight Home Assistant stubs."""
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

    ha_event = types.ModuleType("homeassistant.helpers.event")
    ha_event.async_track_point_in_time = lambda hass, callback, when: (lambda: None)
    sys.modules["homeassistant.helpers.event"] = ha_event

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
    time_semantics.get_next_future_switch = time_semantics.calculate_next_switch
    sys.modules["custom_components.zse_hdo.time_semantics"] = time_semantics

    sensor_path = package_dir / "sensor.py"
    sensor_spec = spec_from_file_location(
        "custom_components.zse_hdo.sensor",
        sensor_path,
    )
    sensor_module = module_from_spec(sensor_spec)
    assert sensor_spec and sensor_spec.loader
    sensor_spec.loader.exec_module(sensor_module)
    return sensor_module


def _stale_payload():
    return {
        "workday": [{"start": "12:00", "end": "13:00", "tariff": "low"}],
        "weekend": [],
        "category": "Domacnost",
        "rate_type": "D3",
        "last_updated": "2026-04-29T12:00:00+00:00",
        "source": "cache",
        "is_stale": True,
        "stale_for_s": 900,
        "consecutive_failures": 2,
        "last_success_at": "2026-04-29T11:45:00+00:00",
        "last_error_at": "2026-04-29T12:00:00+00:00",
        "next_retry_at": "2026-04-29T12:10:00+00:00",
    }


@pytest.mark.parametrize(
    ("entity_attr", "legacy_key"),
    [
        ("ZSEHDOTariffSensor", "hdo_number"),
        ("ZSEHDONextSwitchSensor", "time"),
        ("ZSEHDOTodayScheduleSensor", "period_count"),
    ],
)
def test_existing_entities_expose_stale_metadata(entity_attr, legacy_key):
    module = _load_sensor_module()
    coordinator = types.SimpleNamespace(data=_stale_payload())
    entry = types.SimpleNamespace(entry_id="entry-1")
    entity_cls = getattr(module, entity_attr)
    entity = entity_cls(coordinator, entry, 145)

    attrs = entity.extra_state_attributes

    assert legacy_key in attrs
    assert attrs["is_stale"] is True
    assert attrs["stale_for_s"] == 900
    assert attrs["consecutive_failures"] == 2
    assert attrs["last_success_at"] == "2026-04-29T11:45:00+00:00"
    assert attrs["last_error_at"] == "2026-04-29T12:00:00+00:00"
    assert attrs["next_retry_at"] == "2026-04-29T12:10:00+00:00"


def test_stale_metadata_is_consistent_across_existing_entities():
    module = _load_sensor_module()
    coordinator = types.SimpleNamespace(data=_stale_payload())
    entry = types.SimpleNamespace(entry_id="entry-1")

    entities = [
        module.ZSEHDOTariffSensor(coordinator, entry, 145),
        module.ZSEHDONextSwitchSensor(coordinator, entry, 145),
        module.ZSEHDOTodayScheduleSensor(coordinator, entry, 145),
    ]

    stale_snapshots = [
        {k: v for k, v in entity.extra_state_attributes.items() if "stale" in k or "failures" in k or "retry" in k or "error" in k or "success" in k}
        for entity in entities
    ]

    assert stale_snapshots[0] == stale_snapshots[1] == stale_snapshots[2]


def test_recovery_payload_resets_stale_metadata_on_existing_entities():
    module = _load_sensor_module()
    payload = _stale_payload()
    payload.update(
        {
            "is_stale": False,
            "stale_for_s": 0,
            "consecutive_failures": 0,
            "last_error_at": None,
            "next_retry_at": None,
            "last_success_at": "2026-04-29T12:05:00+00:00",
        }
    )
    coordinator = types.SimpleNamespace(data=payload)
    entry = types.SimpleNamespace(entry_id="entry-1")

    entities = [
        module.ZSEHDOTariffSensor(coordinator, entry, 145),
        module.ZSEHDONextSwitchSensor(coordinator, entry, 145),
        module.ZSEHDOTodayScheduleSensor(coordinator, entry, 145),
    ]

    for entity in entities:
        attrs = entity.extra_state_attributes
        assert attrs["is_stale"] is False
        assert attrs["stale_for_s"] == 0
        assert attrs["consecutive_failures"] == 0
        assert attrs["last_error_at"] is None
        assert attrs["next_retry_at"] is None
