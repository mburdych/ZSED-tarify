# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

Home Assistant custom integration (`custom_components/zse_hdo`) that exposes Slovak ZSE distribution-network HDO (low/high tariff) schedules as HA entities. Distributed via HACS (`hacs.json`). Python is loaded directly by Home Assistant at runtime.

The integration scrapes `https://www.zsdis.sk/Uvod/Online-sluzby/Casy-prepinania-nizkej-a-vysokej-tarify`, extracts two embedded JS arrays (`household_rates`, `business_rates`), and serves one HDO code per config entry.

## Running and testing

Automated parser/coordinator regression tests are available via `pytest`; HA runtime checks remain manual:

- **Smoke-test the parser standalone** (no HA): `python custom_components/zse_hdo/parser.py` — runs the `main()` example which fetches the ZSE page, lists all HDO codes, and prints the schedule for HDO 145.
- **Run automated tests**: `py -m pytest -q tests`
- **In a Home Assistant dev instance**: copy/symlink `custom_components/zse_hdo/` into HA's `config/custom_components/`, restart HA, then add the integration via *Settings → Devices & Services → + Add Integration → "ZSE HDO Live"*. Logs: `Settings → System → Logs` (filter `custom_components.zse_hdo`).
- **Version bumps**: edit `version` in `custom_components/zse_hdo/manifest.json` and add a changelog entry to `README.md` (the README's changelog section is the project's release notes — keep it in sync).

## Architecture

Three layers, one per file, wired together in `__init__.py:async_setup_entry`:

1. **`parser.py` — `ZSEHDOLiveParser`**: pure HTTP/parsing layer. `fetch_page()` GETs the ZSE page; `_extract_javascript_array()` finds `var <name> = [...]` and walks brackets manually (respecting strings/escapes) because the JS is not valid JSON — it then rewrites single→double quotes, quotes bare keys, and strips trailing commas before `json.loads`. `_normalize_schedule()` filters intervals where `t_type == "nt"` (low tariff) and splits them by `weekday`/`weekend` flags. `get_schedule(hdo_number)` returns the dict consumed by the coordinator. Note: `parser.py` has its own `_calculate_current_tariff` and `is_low_tariff_now`, but the sensor layer recomputes the current state itself (see below).

2. **`coordinator.py` — `ZSEHDOCoordinator`**: extends HA's `DataUpdateCoordinator`. Two refresh modes selected by `UPDATE_FREQUENCIES[...]["type"]` in `const.py`:
   - `"interval"` (`5min`, `1hour`) — uses the standard `update_interval`.
   - `"scheduled"` (`1day`, `1week`, `1month`) — sets `update_interval=None` and uses `async_track_point_in_time` to fire at 03:00 (`SCHEDULED_UPDATE_HOUR`) on the appropriate cadence; `_schedule_next_update()` re-arms after each fire. Default frequency is `1week` because the underlying ZSE schedule changes rarely.
   - `_async_update_data` caches the last successful payload in `self._last_known_data` and returns it on fetch errors so entities stay available; only the very first failure (no cache yet) raises `UpdateFailed`.

3. **`sensor.py` — three `CoordinatorEntity` subclasses** registered for the `sensor` platform (the binary sensor is also created from `sensor.py`, not a separate `binary_sensor` platform — `PLATFORMS = ["sensor"]` in `__init__.py`):
   - `ZSEHDOTariffSensor` (binary): recomputes `is_on` on every read from the cached schedule and *current wall-clock time*, including midnight-crossing periods (`end < start`). This is intentional — the coordinator only refreshes the schedule, not the live tariff; sensor evaluation is what makes the state flip at period boundaries without a fetch.
   - `ZSEHDONextSwitchSensor`: same midnight-crossing logic; three-step lookup — currently inside a low period → switch-to-high at its end (advance to tomorrow if the period started before midnight); else next start later today; else tomorrow's first start.
   - `ZSEHDOTodayScheduleSensor`: count + list of today's low-tariff periods, branched on `weekday() >= 5`.

   The midnight-crossing and weekend-vs-workday logic is duplicated across sensors and `parser._calculate_current_tariff`. Keep them in sync when changing one.

4. **`config_flow.py`**: at config time, calls `parser.get_all_hdo_numbers()` to populate the dropdown live from the ZSE page (so newly added HDO codes show up without code changes). Unique-ID is `zse_hdo_<number>` to prevent duplicates. `ZSEHDOOptionsFlowHandler` lets users change `update_frequency` post-setup; it writes back to `config_entry.data` (not `.options`) and triggers `async_reload`.

## Conventions specific to this codebase

- HDO numbers are stored as **integers** throughout (config flow casts the dropdown's string value with `int(...)`); `parser.get_schedule` defensively re-casts because the scraped JSON sometimes has them as strings. Don't reintroduce string comparisons.
- User-visible strings (logs, entity names, attribute values like `tariff_name`, `day_type`) are in Slovak. Code identifiers and docstrings mix Slovak and English — match the surrounding file when editing.
- Every Python file carries the same author/license header block. New files in this package should keep that pattern.
- Translations live in `custom_components/zse_hdo/translations/` (read by HA, not imported). When adding new config-flow strings, add them there too.
- `hacs.json` and `manifest.json` are both required by HACS — keep `version` in `manifest.json` updated for releases.
