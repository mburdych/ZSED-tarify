# AGENTS.md

This file provides guidance to Codex/Cursor agents when working with code in this repository.

## Repository purpose

Home Assistant custom integration (`custom_components/zse_hdo`) that exposes Slovak ZSE distribution-network HDO (low/high tariff) schedules as HA entities. Distributed via HACS (`hacs.json`) — there is no build, no test suite, and no package manifest. Python is loaded directly by Home Assistant at runtime.

The integration scrapes `https://www.zsdis.sk/Uvod/Online-sluzby/Casy-prepinania-nizkej-a-vysokej-tarify`, extracts two embedded JS arrays (`household_rates`, `business_rates`), and serves one HDO code per config entry.

## Running and testing

There is no automated test runner. Iteration is manual:

- **Smoke-test the parser standalone** (no HA): `python custom_components/zse_hdo/parser.py` — runs the `main()` example which fetches the ZSE page, lists all HDO codes, and prints the schedule for HDO 145.
- **In a Home Assistant dev instance**: copy/symlink `custom_components/zse_hdo/` into HA's `config/custom_components/`, restart HA, then add the integration via *Settings -> Devices & Services -> + Add Integration -> "ZSE HDO Live"*. Logs: `Settings -> System -> Logs` (filter `custom_components.zse_hdo`).
- **Version bumps**: edit `version` in `custom_components/zse_hdo/manifest.json` and add a changelog entry to `README.md` (the README changelog section is the project's release notes).

## Architecture

Three layers, one per file, wired together in `__init__.py:async_setup_entry`:

1. **`parser.py` — `ZSEHDOLiveParser`**: pure HTTP/parsing layer. `fetch_page()` GETs the ZSE page; `_extract_javascript_array()` finds `var <name> = [...]` and walks brackets manually (respecting strings/escapes) because the JS is not valid JSON. It then rewrites single->double quotes, quotes bare keys, and strips trailing commas before `json.loads`. `_normalize_schedule()` filters intervals where `t_type == "nt"` and splits by `weekday`/`weekend`. `get_schedule(hdo_number)` returns the dict consumed by the coordinator.
2. **`coordinator.py` — `ZSEHDOCoordinator`**: extends HA `DataUpdateCoordinator`. Supports `interval` and `scheduled` refresh modes from `const.py` and caches last successful payload for fallback on transient failures.
3. **`sensor.py` — entity layer**: exposes tariff status, next switch, and today's schedule from coordinator data. Time-boundary logic handles midnight crossing and weekday/weekend behavior.
4. **`config_flow.py`**: populates HDO choices dynamically from live parser data, enforces unique ID (`zse_hdo_<number>`), and supports changing refresh settings through options flow with entry reload.

## Conventions specific to this codebase

- HDO numbers are stored as integers throughout.
- User-facing text is mostly Slovak; match existing file style.
- Keep translation keys in `custom_components/zse_hdo/translations/` aligned with config/entity changes.
- `hacs.json` and `manifest.json` are both required for releases.
