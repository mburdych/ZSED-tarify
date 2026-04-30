# Phase 3: parser-verification-fixtures - Pattern Map

**Mapped:** 2026-04-29  
**Files analyzed:** 8  
**Analogs found:** 5 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pytest.ini` | config | request-response | None in repo | no-analog |
| `tests/conftest.py` | test | file-I/O | `custom_components/zse_hdo/parser.py` | dataflow-match |
| `tests/fixtures/parser/standard_household_business.html` | test | file-I/O | None in repo | no-analog |
| `tests/fixtures/parser/malformed_js_array.html` | test | file-I/O | None in repo | no-analog |
| `tests/test_parser_extract.py` | test | transform | `custom_components/zse_hdo/parser.py` (`_extract_javascript_array`) | exact-behavior |
| `tests/test_parser_normalize.py` | test | transform | `custom_components/zse_hdo/parser.py` (`_normalize_schedule`) | exact-behavior |
| `tests/test_parser_get_schedule.py` | test | request-response | `custom_components/zse_hdo/parser.py` (`get_schedule`) | exact-behavior |
| `tests/fixtures/parser/missing_var_name.html` | test | file-I/O | `custom_components/zse_hdo/parser.py` (missing var path) | behavior-match |

## Pattern Assignments

### `tests/conftest.py` (test, file-I/O)

**Analog:** `custom_components/zse_hdo/parser.py`

**Imports + parser construction pattern** (lines 14-23, 51-60):
```python
import re
import json
import logging
import time as pytime
from typing import Dict, List, Optional
from datetime import datetime

import aiohttp
import async_timeout

class ZSEHDOLiveParser:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self._own_session = session is None
```

**File/text payload contract pattern** (lines 108-117, 174-176):
```python
def _extract_javascript_array(self, html: str, var_name: str) -> List[Dict]:
    """
    Extrahuje JavaScript array z HTML (napr. var household_rates = [...];)
    """
    # ...
    js_array = html[start_pos:end_pos]
```

**How to apply in new file:** Keep fixture loaders UTF-8 text based and feed whole HTML payload strings into parser methods; do not parse partial fragments in fixtures.

---

### `tests/test_parser_extract.py` (test, transform)

**Analog:** `custom_components/zse_hdo/parser.py` (`_extract_javascript_array`)

**Core extraction pattern** (lines 121-127):
```python
pattern = rf"var\s+{var_name}\s*=\s*\["

match = re.search(pattern, html)
if not match:
    _LOGGER.warning(f"JavaScript variable '{var_name}' not found in HTML")
    return []
```

**Bracket-walk robustness pattern** (lines 138-169):
```python
for i in range(start_pos, len(html)):
    char = html[i]
    if escaped:
        escaped = False
        continue
    if char == '\\':
        escaped = True
        continue
    if char in ['"', "'"]:
        if not in_string:
            in_string = True
            string_char = char
        elif char == string_char:
            in_string = False
            string_char = None
        continue
    if not in_string:
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_pos = i + 1
                break
```

**Error/failure contract pattern** (lines 170-173, 193-199):
```python
if bracket_count != 0:
    _LOGGER.error(f"Unmatched brackets in '{var_name}'")
    return []

try:
    data = json.loads(result)
    return data
except json.JSONDecodeError as err:
    _LOGGER.error(f"Failed to parse JavaScript array '{var_name}': {err}")
    return []
```

**How to apply in new file:** Tests should assert deterministic `[]` on missing var, unmatched brackets, and JSON decode errors.

---

### `tests/test_parser_normalize.py` (test, transform)

**Analog:** `custom_components/zse_hdo/parser.py` (`_normalize_schedule`)

**Output shape pattern** (lines 211-214):
```python
schedule = {
    "workday": [],
    "weekend": []
}
```

**Filtering and mapping pattern** (lines 216-233):
```python
for interval in intervals:
    if interval.get("t_type") != "nt":
        continue  # Preskočiť vysokú tarifu

    period = {
        "start": interval["t_from"],
        "end": interval["t_to"],
        "tariff": "low",
        "meaning": interval.get("meaning", ""),
        "for_rate": interval.get("for_rate", "")
    }

    if interval.get("weekday"):
        schedule["workday"].append(period)
    if interval.get("weekend"):
        schedule["weekend"].append(period)
```

**How to apply in new file:** Tests should check both exclusion (`t_type != "nt"`) and inclusion in both day buckets based on flags.

---

### `tests/test_parser_get_schedule.py` (test, request-response)

**Analog:** `custom_components/zse_hdo/parser.py` (`get_schedule`)

**Composition pattern** (lines 276-282):
```python
html = await self.fetch_page()

household = self._extract_javascript_array(html, "household_rates")
business = self._extract_javascript_array(html, "business_rates")

all_rates = household + business
```

**Type normalization + match pattern** (lines 287-293):
```python
for rate in all_rates:
    rate_code = int(rate["code"]) if isinstance(rate["code"], str) else rate["code"]
    hdo_num = int(hdo_number)

    if rate_code == hdo_num:
        schedule = self._normalize_schedule(rate["intervals"])
```

**Public payload shape + missing case** (lines 303-316):
```python
return {
    "hdo_number": hdo_number,
    "name": f"HDO {hdo_number}",
    "category": "household" if rate in household else "business",
    "rate_type": rate_type,
    "current_tariff": current_tariff,
    "workday": schedule["workday"],
    "weekend": schedule["weekend"],
    "last_updated": dt_util.now().isoformat(),
    "source": ZSE_HDO_URL
}

_LOGGER.warning(f"HDO {hdo_number} not found")
return None
```

**How to apply in new file:** Patch `fetch_page` in tests to return local fixture HTML and assert key set/value semantics plus `None` for missing HDO.

---

### `tests/fixtures/parser/missing_var_name.html` (test fixture, file-I/O)

**Analog:** `custom_components/zse_hdo/parser.py` missing-variable behavior

**Expected behavior source** (lines 123-127):
```python
match = re.search(pattern, html)
if not match:
    _LOGGER.warning(f"JavaScript variable '{var_name}' not found in HTML")
    return []
```

**How to apply in new file:** Fixture should omit one target variable (`household_rates` or `business_rates`) and tests should assert empty extraction list.

## Shared Patterns

### Async parser call boundary
**Source:** `custom_components/zse_hdo/parser.py` (lines 266-280)
**Apply to:** `tests/test_parser_get_schedule.py` async test cases
```python
async def get_schedule(self, hdo_number: int) -> Optional[Dict]:
    html = await self.fetch_page()
    household = self._extract_javascript_array(html, "household_rates")
    business = self._extract_javascript_array(html, "business_rates")
```

### Deterministic failure semantics
**Source:** `custom_components/zse_hdo/parser.py` (lines 124-127, 170-173, 315-316)
**Apply to:** extract + schedule fixture tests
```python
if not match:
    return []
if bracket_count != 0:
    return []
# ...
return None
```

### Time-sensitive output caution
**Source:** `custom_components/zse_hdo/parser.py` and `custom_components/zse_hdo/time_semantics.py` (lines 301, 52-69)
**Apply to:** `tests/test_parser_get_schedule.py`
```python
current_tariff = self._calculate_current_tariff(schedule)
# and in helper:
return "high"
```

Use stable assertions for `current_tariff` (or patch tariff computation) to avoid time-of-day flakes.

## No Analog Found

Files with no close in-repo analog (planner should use `03-RESEARCH.md` guidance directly):

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `pytest.ini` | config | request-response | Repository has no prior pytest config file. |
| `tests/fixtures/parser/standard_household_business.html` | test | file-I/O | No existing fixture corpus or HTML sample files tracked in repo. |
| `tests/fixtures/parser/malformed_js_array.html` | test | file-I/O | No existing malformed-input fixture files. |

## Metadata

**Analog search scope:** `custom_components/zse_hdo/`, `.planning/codebase/TESTING.md`, phase context/research docs  
**Files scanned:** 6 primary files (`03-CONTEXT.md`, `03-RESEARCH.md`, `TESTING.md`, `parser.py`, `time_semantics.py`, `coordinator.py`)  
**Pattern extraction date:** 2026-04-29
