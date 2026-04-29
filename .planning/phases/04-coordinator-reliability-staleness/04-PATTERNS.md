# Phase 4: coordinator-reliability-staleness - Pattern Map

**Mapped:** 2026-04-29
**Files analyzed:** 5
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `custom_components/zse_hdo/coordinator.py` | service | request-response + scheduled | `custom_components/zse_hdo/coordinator.py` | exact |
| `custom_components/zse_hdo/sensor.py` | component | transform + event-driven (`CoordinatorEntity`) | `custom_components/zse_hdo/sensor.py` | exact |
| `custom_components/zse_hdo/const.py` | config | transform | `custom_components/zse_hdo/const.py` | exact |
| `tests/test_coordinator_reliability.py` | test | request-response failure-path | `tests/test_parser_get_schedule.py` | role-match |
| `tests/test_sensor_staleness_attrs.py` | test | transform/contract assertions | `tests/test_parser_normalize.py` | role-match |

## Pattern Assignments

### `custom_components/zse_hdo/coordinator.py` (service, request-response + scheduled)

**Analog:** `custom_components/zse_hdo/coordinator.py`

**Imports pattern** (lines 11-18):
```python
import logging
from datetime import datetime, timedelta, time
from typing import Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util
```

**Frequency config branching pattern** (lines 47-58):
```python
frequency_config = UPDATE_FREQUENCIES.get(
    update_frequency,
    UPDATE_FREQUENCIES[DEFAULT_UPDATE_FREQUENCY]
)

self.frequency_type = frequency_config.get("type", "interval")
self._last_known_data = None

if self.frequency_type == "interval":
    update_interval = timedelta(seconds=frequency_config["seconds"])
```

**Scheduled timer pattern** (lines 128-144):
```python
async def _scheduled_update(now):
    _LOGGER.info(f"HDO {self.hdo_number}: Running scheduled update")
    await self.async_request_refresh()
    self._schedule_next_update()

if hasattr(self, "_scheduled_update_unsub") and self._scheduled_update_unsub:
    self._scheduled_update_unsub()

self._scheduled_update_unsub = async_track_point_in_time(
    self.hass,
    _scheduled_update,
    next_update
)
```

**Error handling + cache fallback pattern** (lines 164-173):
```python
except Exception as err:
    _LOGGER.error(f"Error fetching HDO data for {self.hdo_number}: {err}")

    if self._last_known_data is not None:
        _LOGGER.warning(
            f"HDO {self.hdo_number}: using cached schedule due to fetch error"
        )
        return self._last_known_data

    raise UpdateFailed(f"Error fetching HDO data: {err}")
```

---

### `custom_components/zse_hdo/sensor.py` (component, transform + event-driven)

**Analog:** `custom_components/zse_hdo/sensor.py`

**Imports + helper usage pattern** (lines 16-29):
```python
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .time_semantics import calculate_next_switch, get_periods_for_datetime, is_low_tariff
```

**CoordinatorEntity dynamic calculation pattern** (lines 63-70, 105-111):
```python
@property
def is_on(self) -> bool:
    if not self.coordinator.data:
        return False
    return is_low_tariff(self.coordinator.data, now=dt_util.now())

def _get_next_switch(self) -> Optional[Dict[str, Any]]:
    if not self.coordinator.data:
        return None
    return calculate_next_switch(self.coordinator.data, now=dt_util.now())
```

**Attribute contract pattern for user-visible metadata** (lines 77-85):
```python
return {
    "hdo_number": self._hdo_number,
    "current_tariff": self.coordinator.data.get("current_tariff"),
    "tariff_name": "Nízka tarifa" if self.is_on else "Vysoká tarifa",
    "category": self.coordinator.data.get("category"),
    "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
    "last_updated": self.coordinator.data.get("last_updated"),
    "source": self.coordinator.data.get("source"),
}
```

**Guarded empty-data pattern** (lines 74-75, 124-126, 162-163):
```python
if not self.coordinator.data:
    return {}
```

---

### `custom_components/zse_hdo/const.py` (config, transform)

**Analog:** `custom_components/zse_hdo/const.py`

**Constant table pattern for tunables** (lines 17-23):
```python
UPDATE_FREQUENCIES = {
    "5min": {"label": "Každých 5 minút", "seconds": 300, "type": "interval"},
    "1hour": {"label": "Každú hodinu", "seconds": 3600, "type": "interval"},
    "1day": {"label": "1× denne (03:00)", "seconds": 86400, "type": "scheduled"},
    "1week": {"label": "1× týždenne (pondelok 03:00)", "seconds": 604800, "type": "scheduled"},
    "1month": {"label": "1× mesačne (1. deň 03:00)", "seconds": 2592000, "type": "scheduled"}
}
```

**Default/fallback constant pattern** (lines 25-33):
```python
SCHEDULED_UPDATE_HOUR = 3  # 03:00
DEFAULT_UPDATE_FREQUENCY = "1week"

# Legacy support
UPDATE_INTERVAL = 5  # minutes (deprecated, use CONF_UPDATE_FREQUENCY)
```

---

### `tests/test_coordinator_reliability.py` (test, request-response failure-path)

**Analog:** `tests/test_parser_get_schedule.py`

**Dynamic module load pattern** (lines 11-20):
```python
def _load_parser_module():
    parser_path = Path(__file__).parents[1] / "custom_components" / "zse_hdo" / "parser.py"
    parser_dir = str(parser_path.parent)
    if parser_dir not in sys.path:
        sys.path.insert(0, parser_dir)
    spec = spec_from_file_location("zse_hdo_parser_under_test", parser_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module
```

**Async + patch pattern for behavior contracts** (lines 23-31):
```python
@pytest.mark.asyncio
async def test_get_schedule_returns_expected_contract_keys(standard_parser_html):
    parser_module = _load_parser_module()
    parser = parser_module.ZSEHDOLiveParser()

    with patch.object(parser, "fetch_page", AsyncMock(return_value=standard_parser_html)):
        with patch.object(parser, "_calculate_current_tariff", return_value="low"):
            schedule = await parser.get_schedule(145)
```

**Key assertion style pattern** (lines 33-41):
```python
required_keys = {
    "hdo_number", "category", "workday", "weekend", "current_tariff", "source",
}
assert required_keys.issubset(set(schedule.keys()))
```

---

### `tests/test_sensor_staleness_attrs.py` (test, transform/contract assertions)

**Analog:** `tests/test_parser_normalize.py`

**Arrange-Act-Assert with minimal fixtures pattern** (lines 20-27, 53-60):
```python
def test_normalize_schedule_filters_nt_and_maps_day_buckets():
    parser = _load_parser_class()()
    intervals = [
        # contract input rows
    ]

    schedule = parser._normalize_schedule(intervals)

    assert set(schedule.keys()) == {"workday", "weekend"}
    assert len(schedule["workday"]) == 2
```

**Parameterized invalid-input pattern** from `tests/test_parser_extract.py` (lines 40-55):
```python
@pytest.mark.parametrize(
    ("fixture_name", "var_name"),
    [
        ("missing_var_name.html", "household_rates"),
        ("malformed_js_array.html", "household_rates"),
    ],
)
def test_extract_javascript_array_returns_empty_on_invalid_input(...):
    ...
    assert data == []
```

Use this for stale/fresh variants and empty coordinator payload variants.

## Shared Patterns

### Availability via cached fallback
**Source:** `custom_components/zse_hdo/coordinator.py` (lines 167-173)  
**Apply to:** coordinator reliability logic (`RELI-02`, `RELI-03`)
```python
if self._last_known_data is not None:
    _LOGGER.warning(
        f"HDO {self.hdo_number}: using cached schedule due to fetch error"
    )
    return self._last_known_data

raise UpdateFailed(f"Error fetching HDO data: {err}")
```

### Coordinator-owned timing/scheduling
**Source:** `custom_components/zse_hdo/coordinator.py` (lines 83-115, 117-144)  
**Apply to:** backoff/retry insertion for both interval and scheduled modes
```python
def _calculate_next_update(self) -> datetime:
    now = dt_util.now()
    # branch by self.update_frequency ...
    return next_update

self._scheduled_update_unsub = async_track_point_in_time(
    self.hass, _scheduled_update, next_update
)
```

### Entity metadata surfacing through `extra_state_attributes`
**Source:** `custom_components/zse_hdo/sensor.py` (lines 72-85, 121-133, 160-176)  
**Apply to:** stale flags/age/failure counters required by `RELI-04`
```python
@property
def extra_state_attributes(self) -> Dict[str, Any]:
    if not self.coordinator.data:
        return {}
    return {
        # existing schedule metadata
    }
```

### Shared temporal semantics helper usage
**Source:** `custom_components/zse_hdo/time_semantics.py` (lines 37-43, 45-50, 78-144)  
**Apply to:** avoid duplicating day-type/midnight logic when adding stale-related attributes that depend on current time
```python
def get_periods_for_datetime(schedule, candidate_dt):
    is_weekend = candidate_dt.weekday() >= 5
    return schedule.get("weekend", []) if is_weekend else schedule.get("workday", [])

def is_time_in_period(current_time, start, end):
    if end < start:
        return current_time >= start or current_time < end
    return start <= current_time < end
```

## No Analog Found

None. All likely touched files have direct or strong role-match analogs in current codebase.

## Metadata

**Analog search scope:** `custom_components/zse_hdo/*.py`, `tests/*.py`, phase context/research docs  
**Files scanned:** 13  
**Pattern extraction date:** 2026-04-29
