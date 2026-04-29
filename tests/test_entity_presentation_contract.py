"""Entity presentation contract tests for ZSE HDO sensors."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types


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
    sensor_spec = spec_from_file_location(
        "custom_components.zse_hdo.sensor",
        sensor_path,
    )
    sensor_module = module_from_spec(sensor_spec)
    assert sensor_spec and sensor_spec.loader
    sensor_spec.loader.exec_module(sensor_module)
    return sensor_module


def _coordinator_payload() -> dict:
    return {
        "hdo_number": 145,
        "workday": [{"start": "12:00", "end": "13:00", "tariff": "low"}],
        "weekend": [],
        "current_tariff": "low",
        "category": "Domacnost",
        "rate_type": "D3",
        "last_updated": "2026-04-29T12:00:00+00:00",
        "source": "test_fixture",
        "is_stale": False,
        "stale_for_s": 0,
        "consecutive_failures": 0,
        "last_success_at": "2026-04-29T12:00:00+00:00",
        "last_error_at": None,
        "next_retry_at": None,
    }


def _build_entities():
    module = _load_sensor_module()
    coordinator = types.SimpleNamespace(data=_coordinator_payload())
    entry = types.SimpleNamespace(entry_id="entry-1")
    hdo_number = 145
    return [
        module.ZSEHDOTariffSensor(coordinator, entry, hdo_number),
        module.ZSEHDONextSwitchSensor(coordinator, entry, hdo_number),
        module.ZSEHDOTodayScheduleSensor(coordinator, entry, hdo_number),
    ]


def test_three_entities_surface():
    entities = _build_entities()
    assert len(entities) == 3
    assert sum(1 for entity in entities if entity.__class__.__name__.endswith("TariffSensor")) == 1
    assert sum(1 for entity in entities if entity.__class__.__name__.endswith("NextSwitchSensor")) == 1
    assert sum(1 for entity in entities if entity.__class__.__name__.endswith("TodayScheduleSensor")) == 1


def test_unique_id_contract():
    entities = _build_entities()
    unique_ids = {entity._attr_unique_id for entity in entities}
    assert unique_ids == {
        "zse_hdo_145_tariff",
        "zse_hdo_145_next_switch",
        "zse_hdo_145_today_schedule",
    }


def test_required_attribute_keys_contract():
    entities = _build_entities()
    by_unique_id = {entity._attr_unique_id: entity.extra_state_attributes for entity in entities}

    reliability_keys = {
        "is_stale",
        "stale_for_s",
        "consecutive_failures",
        "last_success_at",
        "last_error_at",
        "next_retry_at",
    }

    assert {"tariff_name", "hdo_number", "current_tariff"}.issubset(
        by_unique_id["zse_hdo_145_tariff"].keys()
    )
    assert {"time", "to_tariff_name"}.issubset(
        by_unique_id["zse_hdo_145_next_switch"].keys()
    )
    assert {"periods", "period_count"}.issubset(
        by_unique_id["zse_hdo_145_today_schedule"].keys()
    )

    for attrs in by_unique_id.values():
        assert reliability_keys.issubset(attrs.keys())
