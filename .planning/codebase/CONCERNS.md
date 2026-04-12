# Codebase Concerns

**Analysis Date:** 2026-04-12

---

## Tech Debt

**Fragile JS-to-JSON conversion in `_extract_javascript_array`:**
- Issue: The method extracts a JS array from raw HTML using bracket counting, then transforms it to valid JSON via a series of regex substitutions. The key-quoting regex (`re.sub(r'(?<!")(\b\w+)(?=\s*:)', r'"\1"', result)`) is brittle — it will silently mangle any JS value that contains word characters immediately before a colon (e.g. `"10:00"` time strings within the array, or nested objects with unusual spacing). The single-quote-to-double-quote replacement (`result.replace("'", '"')`) is also unsafe if any string value contains an apostrophe.
- Files: `custom_components/zse_hdo/parser.py` lines 162–183
- Impact: A minor change to the ZSE website's JS formatting — such as time values written as string keys, or apostrophes in Slovak text labels — will cause `json.loads` to fail and the integration returns empty data silently (returns `[]`). No fallback or alerting exists.
- Fix approach: Use a proper JS-aware parser (e.g. `demjson3` or `chompjs`) instead of regex substitution chains, or snapshot and test against the actual HTML structure.

**Duplicate `_parse_time` method:**
- Issue: An identical `_parse_time(time_str: str) -> time` method is defined in two separate classes: `ZSEHDOLiveParser` (`custom_components/zse_hdo/parser.py` line 185) and `ZSEHDONextSwitchSensor` (`custom_components/zse_hdo/sensor.py` line 103). Both perform `hour, minute = map(int, time_str.split(':'))` with no error handling.
- Files: `custom_components/zse_hdo/parser.py:185`, `custom_components/zse_hdo/sensor.py:103`
- Impact: Any bug fix or format-handling improvement (e.g. supporting seconds `HH:MM:SS`) must be applied in two places. A malformed time string raises an unhandled `ValueError` that propagates to the caller.
- Fix approach: Extract to a module-level utility function in `parser.py` and import it in `sensor.py`.

**`is_low_tariff_now()` duplicates `_calculate_current_tariff()` logic:**
- Issue: `is_low_tariff_now()` in `parser.py` (lines 368–400) re-implements the same midnight-crossover-aware interval check that `_calculate_current_tariff()` already performs (lines 233–268). Both call `datetime.now()` independently and iterate over periods with identical logic.
- Files: `custom_components/zse_hdo/parser.py:233–268` and `parser.py:368–400`
- Impact: The two methods can theoretically return inconsistent results if called near a tariff boundary (different `datetime.now()` snapshots). Any logic fix must be applied twice.
- Fix approach: Have `is_low_tariff_now()` call `get_schedule()` and then delegate to `_calculate_current_tariff(schedule)`, eliminating the duplicated loop entirely.

**`UPDATE_INTERVAL` legacy constant not removed:**
- Issue: `const.py` line 32 defines `UPDATE_INTERVAL = 5` and marks it as deprecated, but it is not imported or used anywhere in the current codebase.
- Files: `custom_components/zse_hdo/const.py:32`
- Impact: Dead code with a misleading comment implies there was a prior approach still in play. New contributors may attempt to use it.
- Fix approach: Remove the constant.

**Scheduled mode uses a 5-minute fallback `update_interval`:**
- Issue: When `frequency_type == "scheduled"` (1day / 1week / 1month), the `DataUpdateCoordinator` is still initialized with `update_interval=timedelta(minutes=5)` as a fallback (`coordinator.py` line 65). This means HA's built-in coordinator polling fires every 5 minutes regardless, performing unnecessary HTTP fetches to the ZSE website until the custom timer fires.
- Files: `custom_components/zse_hdo/coordinator.py:64–66`
- Impact: Users who select "1× weekly" or "1× monthly" will generate far more web requests than intended — up to 288 per day instead of 1.
- Fix approach: Set `update_interval=None` or a large value (e.g. `timedelta(days=400)`) for scheduled types so the HA coordinator does not poll autonomously. Rely solely on `async_track_point_in_time` for scheduled refreshes.

---

## Known Bugs

**`_get_next_switch` logic is incorrect for periods already passed today:**
- Symptoms: The next-switch sensor can return a stale or wrong switch time. The method in `sensor.py` iterates `sorted_periods` and returns the first `start > current_time`, but it does not account for the case where the current time is already past all periods for today — it falls back to "tomorrow's first period" but does not check if tomorrow is a weekend vs weekday.
- Files: `custom_components/zse_hdo/sensor.py:108–158`
- Trigger: After the last low-tariff period ends on a given day, particularly at weekday/weekend boundaries (e.g. Friday evening → Saturday).
- Workaround: None; the sensor will display an incorrect next-switch time until midnight.

**`_get_next_switch` calls `_get_next_switch()` twice per HA state update cycle:**
- Symptoms: `native_value` (line 163) and `extra_state_attributes` (line 172) each independently call `self._get_next_switch()`, which in turn calls `datetime.now()` twice. Results can differ if the call spans a second boundary.
- Files: `custom_components/zse_hdo/sensor.py:160–180`
- Trigger: Any state update cycle; race is theoretical but the double computation is always wasteful.
- Workaround: None.

---

## Security Considerations

**No input validation on `hdo_number` before network use:**
- Risk: `config_flow.py` converts `user_input[CONF_HDO_NUMBER]` directly to `int` (line 50) with no try/except. If the dropdown is bypassed (e.g. via direct API call to HA), a non-integer value raises an unhandled `ValueError` that could crash the config flow.
- Files: `custom_components/zse_hdo/config_flow.py:50`
- Current mitigation: The UI constrains the input via `vol.In(...)`, which provides partial protection under normal use.
- Recommendations: Wrap the `int()` conversion in a try/except and return a validation error.

**No rate limiting or circuit breaker on ZSE web scraping:**
- Risk: The integration scrapes `https://www.zsdis.sk/...` on every coordinator refresh. With `5min` update frequency selected, this is 12 requests/hour per configured HDO. If the ZSE website changes its rate limiting policy or the IP is blocked, the integration will log repeated errors but keep retrying at full frequency indefinitely.
- Files: `custom_components/zse_hdo/parser.py:56–90`, `custom_components/zse_hdo/coordinator.py:145–168`
- Current mitigation: `REQUEST_TIMEOUT = 30` prevents hanging connections.
- Recommendations: Implement exponential backoff on `aiohttp.ClientError` (e.g. back off to hourly after 3 consecutive failures). Consider caching the last successful HTML response.

**`get_schedule()` fetches the full page twice when called from `is_low_tariff_now()`:**
- Risk: `is_low_tariff_now()` calls `get_schedule()` which calls `fetch_page()` which makes an HTTP request. `get_schedule()` itself already duplicates the page fetch across `get_all_hdo_numbers()` and similar methods — each call is an independent HTTP round-trip with no caching.
- Files: `custom_components/zse_hdo/parser.py:288–338`, `parser.py:368–400`
- Current mitigation: None.
- Recommendations: Add an instance-level page cache with a short TTL (e.g. 60 seconds) to deduplicate HTTP calls within a single update cycle.

---

## Performance Bottlenecks

**Full HTML page fetched on every operation, no caching:**
- Problem: `fetch_page()` is called independently by `get_all_hdo_numbers()`, `get_schedule()`, and `get_all_schedules()`. Each call downloads the entire ZSE HTML page (unknown size). During config flow setup, `get_all_hdo_numbers()` fetches the page once, and then `get_schedule()` fetches it again during `async_config_entry_first_refresh()`.
- Files: `custom_components/zse_hdo/parser.py:56–90`, `parser.py:270–286`, `parser.py:288–338`
- Cause: No result or response caching exists at any layer.
- Improvement path: Cache the fetched HTML for at minimum the duration of a single event loop iteration (using an instance variable reset on each `fetch_page()` call) or a configurable TTL.

**`_get_next_switch` re-sorts periods on every property access:**
- Problem: `sorted(periods, key=lambda p: self._parse_time(p["start"]))` is called every time `native_value` or `extra_state_attributes` is accessed, which happens on every HA state refresh cycle.
- Files: `custom_components/zse_hdo/sensor.py:121`
- Cause: No caching of sorted periods; schedule data from coordinator does not pre-sort.
- Improvement path: Sort periods once during `_normalize_schedule()` in `parser.py` so the coordinator data is already sorted.

---

## Fragile Areas

**JS array extraction tied to exact website structure:**
- Files: `custom_components/zse_hdo/parser.py:92–183`
- Why fragile: The entire integration depends on two specific JavaScript variable names (`household_rates`, `business_rates`) existing in the ZSE HTML with a specific format. Any website redesign, minification, variable rename, or migration to a JSON API would silently return empty schedules. The bracket-counting parser also does not handle template literals (backtick strings), JS comments inside the array, or multi-line escaped strings.
- Safe modification: Always test changes against a locally saved copy of the live HTML page.
- Test coverage: None.

**`_scheduled_update_unsub` not cancelled on integration unload:**
- Files: `custom_components/zse_hdo/__init__.py:72–78`, `custom_components/zse_hdo/coordinator.py:116–143`
- Why fragile: `async_unload_entry` in `__init__.py` unloads platforms and removes `hass.data` but never calls `coordinator._scheduled_update_unsub()`. If the integration is unloaded while a scheduled timer is pending, the `async_track_point_in_time` callback will still fire and attempt `self.async_request_refresh()` on a coordinator that is no longer active.
- Safe modification: Add an `async_shutdown` or `async_close` method to the coordinator that cancels the unsub, and call it from `async_unload_entry`.
- Test coverage: None.

**`_schedule_next_update` called during `__init__` before `self.hass` is available:**
- Files: `custom_components/zse_hdo/coordinator.py:79–80`
- Why fragile: `DataUpdateCoordinator.__init__` assigns `self.hass` from the `hass` parameter during `super().__init__()` call at line 71. `_schedule_next_update()` is called at line 80, after `super().__init__()`, so `self.hass` is available — but this ordering is implicit and fragile. If `super().__init__()` is ever moved below line 80 in a refactor, `async_track_point_in_time(self.hass, ...)` will raise `AttributeError`.
- Safe modification: Add a comment explicitly noting the dependency on `super().__init__()` completing first.
- Test coverage: None.

---

## Timezone Handling

**`datetime.now()` used instead of `dt_util.now()` throughout parser and sensor:**
- Issue: `parser.py` uses `datetime.now()` at lines 245, 333, and 382. `sensor.py` uses `datetime.now()` at lines 113, 201, and 213. `coordinator.py` correctly uses `dt_util.now()` only for `_calculate_next_update()` (line 84).
- Files: `custom_components/zse_hdo/parser.py:245,333,382`, `custom_components/zse_hdo/sensor.py:113,201,213`
- Impact: `datetime.now()` returns local system time, not the timezone configured in Home Assistant. On a HA instance where the system timezone differs from the configured HA timezone (common on servers, Docker containers, or NAS devices), tariff calculations will be wrong. The `last_updated` timestamp stored in coordinator data will also be in a different timezone than other HA entities. This is a correctness bug for multi-timezone deployments.
- Fix approach: Replace all `datetime.now()` calls with `dt_util.now()` (already imported in `coordinator.py`). Add `from homeassistant.util import dt as dt_util` to `parser.py` and `sensor.py`.

---

## Test Coverage Gaps

**No test suite exists:**
- What's not tested: All parsing logic, bracket-counting extraction, JS-to-JSON conversion, tariff calculation, midnight crossover handling, next-switch calculation, scheduled update firing, coordinator initialization, sensor state values, config flow validation.
- Files: All files under `custom_components/zse_hdo/`
- Risk: Any change to the ZSE website HTML structure, or any refactor of the parsing logic, will produce a silent regression with no automated detection. The midnight-crossover tariff calculation in `_calculate_current_tariff()` and `is_low_tariff_now()` is especially risky to test manually.
- Priority: High — the JS extraction and tariff calculation logic are the most critical and most likely to break silently.

---

*Concerns audit: 2026-04-12*
