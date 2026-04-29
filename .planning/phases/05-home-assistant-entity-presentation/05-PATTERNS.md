# Phase 5: home-assistant-entity-presentation - Pattern Map

**Mapped:** 2026-04-29  
**Files analyzed:** 4  
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `custom_components/zse_hdo/sensor.py` | component | transform | `custom_components/zse_hdo/sensor.py` | exact |
| `tests/test_entity_presentation_contract.py` | test | transform | `tests/test_sensor_staleness_attrs.py` | exact |
| `README.md` | config | request-response | `README.md` | exact |
| `EXAMPLES.md` | config | request-response | `EXAMPLES.md` | exact |

## Pattern Assignments

### `custom_components/zse_hdo/sensor.py` (component, transform)

**Analog:** `custom_components/zse_hdo/sensor.py`

**Imports pattern** (lines 13-29):
```python
import logging
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .time_semantics import calculate_next_switch, get_periods_for_datetime, is_low_tariff
```

**Entity identity pattern** (lines 71-73, 114-116, 163-165):
```python
self._attr_unique_id = f"zse_hdo_{hdo_number}_tariff"
self._attr_name = f"ZSE HDO {hdo_number} Tarifa"
self._attr_device_class = BinarySensorDeviceClass.POWER

self._attr_unique_id = f"zse_hdo_{hdo_number}_next_switch"
self._attr_name = f"ZSE HDO {hdo_number} Ďalšie prepnutie"
self._attr_icon = "mdi:clock-outline"

self._attr_unique_id = f"zse_hdo_{hdo_number}_today_schedule"
self._attr_name = f"ZSE HDO {hdo_number} Dnešný rozvrh"
self._attr_icon = "mdi:calendar-today"
```

**Reliability projection pattern** (lines 33-42, 89-98, 146-152, 190-197):
```python
def _reliability_attrs(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "is_stale": data.get("is_stale", False),
        "stale_for_s": data.get("stale_for_s", 0),
        "consecutive_failures": data.get("consecutive_failures", 0),
        "last_success_at": data.get("last_success_at"),
        "last_error_at": data.get("last_error_at"),
        "next_retry_at": data.get("next_retry_at"),
    }

return {
    "hdo_number": self._hdo_number,
    "current_tariff": self.coordinator.data.get("current_tariff"),
    "tariff_name": "Nízka tarifa" if self.is_on else "Vysoká tarifa",
    ...
    **_reliability_attrs(self.coordinator.data),
}
```

**Time semantics usage pattern** (lines 81, 123, 176-177):
```python
return is_low_tariff(self.coordinator.data, now=dt_util.now())
return calculate_next_switch(self.coordinator.data, now=dt_util.now())
periods = get_periods_for_datetime(self.coordinator.data, now)
```

---

### `tests/test_entity_presentation_contract.py` (test, transform)

**Analog:** `tests/test_sensor_staleness_attrs.py` (primary), `tests/test_coordinator_reliability.py` (secondary)

**HA stub-loading pattern** (from `tests/test_sensor_staleness_attrs.py`, lines 14-97):
```python
def _load_sensor_module():
    root = Path(__file__).parents[1]
    package_dir = root / "custom_components" / "zse_hdo"
    ...
    sensor_spec = spec_from_file_location(
        "custom_components.zse_hdo.sensor",
        sensor_path,
    )
    sensor_module = module_from_spec(sensor_spec)
    assert sensor_spec and sensor_spec.loader
    sensor_spec.loader.exec_module(sensor_module)
    return sensor_module
```

**Contract assertion style** (from `tests/test_sensor_staleness_attrs.py`, lines 124-139):
```python
attrs = entity.extra_state_attributes

assert legacy_key in attrs
assert attrs["is_stale"] is True
assert attrs["stale_for_s"] == 900
assert attrs["consecutive_failures"] == 2
assert attrs["last_success_at"] == "2026-04-29T11:45:00+00:00"
assert attrs["last_error_at"] == "2026-04-29T12:00:00+00:00"
assert attrs["next_retry_at"] == "2026-04-29T12:10:00+00:00"
```

**Recovery/reset contract pattern** (from `tests/test_sensor_staleness_attrs.py`, lines 161-190):
```python
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
...
assert attrs["is_stale"] is False
assert attrs["stale_for_s"] == 0
assert attrs["consecutive_failures"] == 0
```

**Async reliability assertion style** (from `tests/test_coordinator_reliability.py`, lines 160-166, 206-211):
```python
assert cached["is_stale"] is True
assert cached["stale_for_s"] == 2100
assert cached["last_success_at"] == t0.isoformat()
assert cached["last_error_at"] == t1.isoformat()
assert cached["consecutive_failures"] == 1
assert cached["next_retry_at"] is not None

assert recovered["is_stale"] is False
assert recovered["stale_for_s"] == 0
assert recovered["consecutive_failures"] == 0
assert recovered["last_error_at"] is None
assert recovered["next_retry_at"] is None
```

---

### `README.md` (config, request-response)

**Analog:** `README.md`

**Entity contract documentation pattern** (lines 51-94):
```markdown
## 📊 Entity

### 1. Binary Sensor - Aktuálna tarifa
- **Entity ID**: `binary_sensor.zse_hdo_XXX_tariff`
- **Atribúty**:
  - `hdo_number`
  - `current_tariff`
  - `tariff_name`
  - `category`
  - `rate_type`
  - `last_updated`
  - `is_stale`
  - `stale_for_s`
  - `consecutive_failures`
  - `last_success_at`
  - `last_error_at`
  - `next_retry_at`
```

**Baseline card example pattern** (lines 134-146):
```yaml
type: entities
title: ZSE HDO 145
entities:
  - entity: binary_sensor.zse_hdo_145_tariff
  - entity: sensor.zse_hdo_145_next_switch
  - entity: sensor.zse_hdo_145_today_schedule
```

---

### `EXAMPLES.md` (config, request-response)

**Analog:** `EXAMPLES.md`

**Entities-card baseline pattern** (lines 7-18):
```yaml
type: entities
title: "⚡ ZSE HDO 145"
entities:
  - entity: binary_sensor.zse_hdo_145_tariff
  - entity: sensor.zse_hdo_145_next_switch
  - entity: sensor.zse_hdo_145_today_schedule
```

**Template attr-consumption pattern** (lines 55-63, 69-70):
```yaml
secondary_info: |
  {{ state_attr('binary_sensor.zse_hdo_145_tariff', 'tariff_name') }}

secondary: |
  {{ state_attr('sensor.zse_hdo_145_next_switch', 'time') }}
  → {{ state_attr('sensor.zse_hdo_145_next_switch', 'to_tariff_name') }}

secondary: |
  {{ states('sensor.zse_hdo_145_today_schedule') }} období
  ({{ state_attr('sensor.zse_hdo_145_today_schedule', 'day_type') }})
```

## Shared Patterns

### Stable Entity IDs and Unique IDs
**Source:** `custom_components/zse_hdo/sensor.py`  
**Apply to:** `sensor.py` edits + new presentation contract tests
```python
self._attr_unique_id = f"zse_hdo_{hdo_number}_tariff"
self._attr_unique_id = f"zse_hdo_{hdo_number}_next_switch"
self._attr_unique_id = f"zse_hdo_{hdo_number}_today_schedule"
```

### Reliability Metadata Contract
**Source:** `custom_components/zse_hdo/sensor.py` + `custom_components/zse_hdo/coordinator.py`  
**Apply to:** all three entity contract assertions + README/EXAMPLES parity checks
```python
# sensor.py
"is_stale": data.get("is_stale", False),
"stale_for_s": data.get("stale_for_s", 0),
"consecutive_failures": data.get("consecutive_failures", 0),
"last_success_at": data.get("last_success_at"),
"last_error_at": data.get("last_error_at"),
"next_retry_at": data.get("next_retry_at"),

# coordinator.py
payload["is_stale"] = is_stale
payload["stale_for_s"] = self._calculate_stale_for_seconds(now) if is_stale else 0
payload["next_retry_at"] = (
    self._next_retry_at.isoformat() if self._next_retry_at else None
)
```

### Docs-to-Entity Parity
**Source:** `README.md`, `EXAMPLES.md`, `tests/test_sensor_staleness_attrs.py`  
**Apply to:** `tests/test_entity_presentation_contract.py`
```python
# follow direct key assertions, not loose snapshot text matching
assert "tariff_name" in tariff_attrs
assert "time" in next_switch_attrs
assert "period_count" in today_schedule_attrs
assert "is_stale" in tariff_attrs
assert "next_retry_at" in next_switch_attrs
```

## No Analog Found

None.

## Metadata

**Analog search scope:** `custom_components/zse_hdo/`, `tests/`, `README.md`, `EXAMPLES.md`, `.planning/phases/05-home-assistant-entity-presentation/05-RESEARCH.md`  
**Files scanned:** 8  
**Pattern extraction date:** 2026-04-29
