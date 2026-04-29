# Phase 2: tariff-time-semantics - Pattern Map

**Mapped:** 2026-04-29  
**Files analyzed:** 3  
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `custom_components/zse_hdo/time_semantics.py` | utility | transform | `custom_components/zse_hdo/sensor.py` | exact |
| `custom_components/zse_hdo/parser.py` | service | request-response + transform | `custom_components/zse_hdo/parser.py` | exact |
| `custom_components/zse_hdo/sensor.py` | component | event-driven + transform | `custom_components/zse_hdo/sensor.py` | exact |

## Pattern Assignments

### `custom_components/zse_hdo/time_semantics.py` (utility, transform)

**Analog:** `custom_components/zse_hdo/sensor.py` (primary) + `custom_components/zse_hdo/parser.py` (secondary)

**Imports + helper shape pattern** (`sensor.py`, lines 13-16 and 62-66):
```python
import logging
from datetime import datetime, time, timedelta
from typing import Any, Dict, Optional

def _parse_time(self, time_str: str) -> time:
    """Parse time string to time object."""
    hour, minute = map(int, time_str.split(':'))
    return time(hour=hour, minute=minute)
```

**Midnight-crossing inclusion rule (canonical logic to centralize)** (`sensor.py`, lines 83-89):
```python
if end < start:  # midnight crossing
    if current_time >= start or current_time < end:
        return True
else:
    if start <= current_time < end:
        return True
```

**Next-switch 3-step search pattern** (`sensor.py`, lines 142-195):
```python
# Step 1: currently in low period -> next switch is end of current period
for period in periods:
    start = self._parse_time(period["start"])
    end = self._parse_time(period["end"])
    # ... in_period check incl. midnight crossing ...
    if in_period:
        end_dt = datetime.combine(now.date(), end)
        if end < start and current_time >= start:
            end_dt = datetime.combine(now.date() + timedelta(days=1), end)
        return {"datetime": end_dt, "to_tariff": "high", "period": period}

# Step 2: next start later today
candidates = []
for period in periods:
    start = self._parse_time(period["start"])
    if start > current_time:
        candidates.append((datetime.combine(now.date(), start), period))

# Step 3: fallback to tomorrow first period
sorted_periods = sorted(periods, key=lambda p: self._parse_time(p["start"]))
```

**Parser-side duplicate tariff logic to absorb into utility** (`parser.py`, lines 233-268):
```python
def _calculate_current_tariff(self, schedule: Dict[str, List[Dict]]) -> str:
    now = datetime.now()
    current_time = now.time()
    is_weekend = now.weekday() >= 5
    periods = schedule["weekend"] if is_weekend else schedule["workday"]
    for period in periods:
        start = self._parse_time(period["start"])
        end = self._parse_time(period["end"])
        if end < start:
            if current_time >= start or current_time < end:
                return "low"
        else:
            if start <= current_time < end:
                return "low"
    return "high"
```

**Timezone source pattern to copy** (`coordinator.py`, lines 18 and 85):
```python
from homeassistant.util import dt as dt_util

now = dt_util.now()
```

---

### `custom_components/zse_hdo/parser.py` (service, request-response + transform)

**Analog:** `custom_components/zse_hdo/parser.py`

**HTTP fetch + timeout + error handling pattern** (lines 66-90):
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sk,en;q=0.5",
}

try:
    async with async_timeout.timeout(REQUEST_TIMEOUT):
        async with self._session.get(ZSE_HDO_URL, headers=headers) as response:
            response.raise_for_status()
            html = await response.text()
            return html
except aiohttp.ClientError as err:
    _LOGGER.error(f"Failed to fetch HDO data: {err}")
    raise
```

**Schedule normalization pattern (preserve output schema)** (lines 208-231):
```python
schedule = {
    "workday": [],
    "weekend": []
}

for interval in intervals:
    if interval.get("t_type") != "nt":
        continue
    period = {
        "start": interval["t_from"],
        "end": interval["t_to"],
        "tariff": "low",
        "meaning": interval.get("meaning", ""),
        "for_rate": interval.get("for_rate", "")
    }
```

**Response payload contract pattern (must remain stable)** (lines 325-335):
```python
return {
    "hdo_number": hdo_number,
    "name": f"HDO {hdo_number}",
    "category": "household" if rate in household else "business",
    "rate_type": rate_type,
    "current_tariff": current_tariff,
    "workday": schedule["workday"],
    "weekend": schedule["weekend"],
    "last_updated": datetime.now().isoformat(),
    "source": ZSE_HDO_URL
}
```

**Type-safe HDO comparison pattern** (lines 309-315):
```python
rate_code = int(rate["code"]) if isinstance(rate["code"], str) else rate["code"]
hdo_num = int(hdo_number)
if rate_code == hdo_num:
    schedule = self._normalize_schedule(rate["intervals"])
```

---

### `custom_components/zse_hdo/sensor.py` (component, event-driven + transform)

**Analog:** `custom_components/zse_hdo/sensor.py`

**Entity setup pattern (single platform, 3 entities)** (lines 32-47):
```python
async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    hdo_number = hass.data[DOMAIN][entry.entry_id]["hdo_number"]
    entities = [
        ZSEHDOTariffSensor(coordinator, entry, hdo_number),
        ZSEHDONextSwitchSensor(coordinator, entry, hdo_number),
        ZSEHDOTodayScheduleSensor(coordinator, entry, hdo_number),
    ]
    async_add_entities(entities)
```

**Dynamic current-state evaluation pattern** (lines 68-90):
```python
@property
def is_on(self) -> bool:
    if not self.coordinator.data:
        return False
    now = datetime.now()
    current_time = now.time()
    is_weekend = now.weekday() >= 5
    periods = self.coordinator.data["weekend"] if is_weekend else self.coordinator.data["workday"]
    # ... period iteration with midnight crossing ...
```

**Next-switch attribute shape to preserve** (lines 214-219):
```python
return {
    "time": next_switch["time"],
    "to_tariff": next_switch["to_tariff"],
    "to_tariff_name": "Nízka tarifa" if next_switch["to_tariff"] == "low" else "Vysoká tarifa",
    "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
}
```

**Today schedule day-type selection pattern** (lines 252-263):
```python
now = datetime.now()
is_weekend = now.weekday() >= 5
periods = self.coordinator.data["weekend"] if is_weekend else self.coordinator.data["workday"]

return {
    "day_type": "Víkend" if is_weekend else "Pracovný deň",
    "periods": periods,
    "period_count": len(periods),
}
```

## Shared Patterns

### Home Assistant timezone source
**Source:** `custom_components/zse_hdo/coordinator.py` (lines 18, 85)  
**Apply to:** `time_semantics.py`, `parser.py`, `sensor.py`
```python
from homeassistant.util import dt as dt_util
now = dt_util.now()
```

### Midnight-crossing tariff predicate
**Source:** `custom_components/zse_hdo/sensor.py` (lines 83-89), `custom_components/zse_hdo/parser.py` (lines 257-265)  
**Apply to:** shared helper + both parser/sensor call sites
```python
if end < start:
    in_period = current_time >= start or current_time < end
else:
    in_period = start <= current_time < end
```

### Day-type branch (workday vs weekend)
**Source:** `custom_components/zse_hdo/sensor.py` (lines 240-244), `custom_components/zse_hdo/parser.py` (lines 247-251)  
**Apply to:** shared helper functions requiring period set selection
```python
is_weekend = now.weekday() >= 5
periods = schedule["weekend"] if is_weekend else schedule["workday"]
```

### Stable payload/entity contract
**Source:** `custom_components/zse_hdo/parser.py` (lines 325-335), `custom_components/zse_hdo/sensor.py` (lines 98-106, 214-219, 257-263)  
**Apply to:** all refactor edits in this phase
```python
"current_tariff": current_tariff
"workday": schedule["workday"]
"weekend": schedule["weekend"]
"day_type": "Víkend" if is_weekend else "Pracovný deň"
```

## No Analog Found

None. All likely Phase 2 files have direct analogs in current code.

## Metadata

**Analog search scope:** `custom_components/zse_hdo/`  
**Files scanned:** 6 (`__init__.py`, `const.py`, `config_flow.py`, `coordinator.py`, `parser.py`, `sensor.py`)  
**Pattern extraction date:** 2026-04-29
