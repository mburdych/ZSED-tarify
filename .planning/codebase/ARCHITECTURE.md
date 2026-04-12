# Architecture

**Analysis Date:** 2026-04-12

## Pattern Overview

**Overall:** Home Assistant Custom Integration — DataUpdateCoordinator pattern

**Key Characteristics:**
- Single-platform integration (sensor platform only; binary sensors are registered as part of the sensor platform via `PLATFORMS = ["sensor"]`)
- Coordinator-driven data fetching: all entities are passive `CoordinatorEntity` subscribers — they do not fetch data themselves
- Scraping-based data source: no public API, HTML is fetched and inline JavaScript arrays are extracted and converted to JSON
- Two scheduling modes controlled by config: interval-based (5 min / 1 hour) and calendar-scheduled (daily / weekly / monthly at 03:00)
- Multi-instance capable: each configured HDO number gets its own coordinator stored under `hass.data[DOMAIN][entry.entry_id]`

## Layers

**Data Fetching Layer:**
- Purpose: HTTP scraping of the ZSE website and JS-to-JSON parsing
- Location: `custom_components/zse_hdo/parser.py`
- Contains: `ZSEHDOLiveParser` class
- Depends on: `aiohttp`, `async_timeout`, `re`, `json`
- Used by: `ZSEHDOCoordinator`, `ZSEHDOConfigFlow` (for discovery of available HDO numbers)

**Coordination Layer:**
- Purpose: Schedules and owns refresh cycles; translates parser output into HA coordinator data dict
- Location: `custom_components/zse_hdo/coordinator.py`
- Contains: `ZSEHDOCoordinator(DataUpdateCoordinator)`
- Depends on: `ZSEHDOLiveParser`, `homeassistant.helpers.update_coordinator`, `homeassistant.helpers.event.async_track_point_in_time`
- Used by: `__init__.py` (created here), `sensor.py` (consumed here)

**Entity Layer:**
- Purpose: Exposes coordinator data as HA entities
- Location: `custom_components/zse_hdo/sensor.py`
- Contains: `ZSEHDOTariffSensor`, `ZSEHDONextSwitchSensor`, `ZSEHDOTodayScheduleSensor`
- Depends on: `ZSEHDOCoordinator` (via `CoordinatorEntity`), `homeassistant.components.binary_sensor`, `homeassistant.components.sensor`
- Used by: HA platform setup via `async_setup_entry`

**Configuration Layer:**
- Purpose: UI-driven config flow for selecting HDO number and update frequency
- Location: `custom_components/zse_hdo/config_flow.py`
- Contains: `ZSEHDOConfigFlow(ConfigFlow)`, `ZSEHDOOptionsFlowHandler(OptionsFlow)`
- Depends on: `ZSEHDOLiveParser` (fetches available HDO numbers live during setup), `voluptuous`, `const.py`
- Used by: HA config entry registration

**Integration Bootstrap:**
- Purpose: Wires parser, coordinator, and platform together on entry load/unload
- Location: `custom_components/zse_hdo/__init__.py`
- Contains: `async_setup_entry`, `async_unload_entry`
- Depends on: All layers above

**Constants:**
- Purpose: Centralised domain name, config keys, update frequency definitions
- Location: `custom_components/zse_hdo/const.py`
- Used by: All other modules

## Data Flow

**Initial Setup:**
1. User opens HA Integrations UI — `ZSEHDOConfigFlow.async_step_user` fires
2. Config flow instantiates `ZSEHDOLiveParser` and calls `get_all_hdo_numbers()` to populate the HDO dropdown
3. User selects HDO number + update frequency; entry is saved via `async_create_entry`
4. HA calls `async_setup_entry` in `__init__.py`
5. `ZSEHDOLiveParser` and `ZSEHDOCoordinator` are instantiated and stored in `hass.data[DOMAIN][entry.entry_id]`
6. `coordinator.async_config_entry_first_refresh()` triggers the first data fetch
7. HA forwards setup to the `sensor` platform — `sensor.async_setup_entry` creates all three entities

**Per-Update Cycle (interval mode):**
1. HA scheduler fires `ZSEHDOCoordinator._async_update_data` at the configured interval
2. Coordinator calls `parser.get_schedule(hdo_number)`
3. Parser calls `fetch_page()` → HTTP GET to `https://www.zsdis.sk/...`
4. Parser extracts `household_rates` and `business_rates` JS arrays via `_extract_javascript_array`
5. Matching rate entry is found by `code`; `_normalize_schedule` filters only `nt` (low-tariff) intervals into `workday`/`weekend` lists
6. `_calculate_current_tariff` computes `"low"` or `"high"` from current local time
7. Coordinator stores result dict in `self.data`; all `CoordinatorEntity` listeners are notified
8. Entity properties (`is_on`, `native_value`, `extra_state_attributes`) recompute from `coordinator.data` on demand

**Per-Update Cycle (scheduled mode):**
- Same as above, but step 1 is triggered by `async_track_point_in_time` callback registered in `_schedule_next_update`
- After each scheduled refresh, `_schedule_next_update` is called again to set the next point-in-time trigger
- The base `DataUpdateCoordinator` `update_interval` is set to 5 minutes as a fallback but is not the primary driver

**State Management:**
- All mutable runtime state lives inside `ZSEHDOCoordinator.data` (a plain `Dict`)
- Entities hold no state themselves; every property reads directly from `coordinator.data`
- Config entry data persisted by HA: `hdo_number` (int), `update_frequency` (str key)

## Key Abstractions

**Schedule Dict:**
- Purpose: Canonical normalised form of one HDO entry
- Produced by: `parser.get_schedule()` → returned from `_async_update_data`
- Shape:
  ```python
  {
      "hdo_number": int,
      "name": str,
      "category": "household" | "business",
      "rate_type": str,
      "current_tariff": "low" | "high",
      "workday": [{"start": "HH:MM", "end": "HH:MM", "tariff": "low", ...}],
      "weekend": [...],
      "last_updated": ISO8601 str,
      "source": str (URL)
  }
  ```
- Consumed by: All three entity classes in `sensor.py`

**UPDATE_FREQUENCIES registry:**
- Purpose: Maps frequency keys to scheduling metadata
- Location: `custom_components/zse_hdo/const.py`
- Shape: `{"5min": {"label": str, "seconds": int, "type": "interval"|"scheduled"}, ...}`
- Controls coordinator init path and scheduling mode selection

## Entry Points

**Integration Load:**
- Location: `custom_components/zse_hdo/__init__.py` — `async_setup_entry`
- Triggers: HA loading a saved config entry
- Responsibilities: Create parser and coordinator, run first refresh, register sensor platform

**Integration Unload:**
- Location: `custom_components/zse_hdo/__init__.py` — `async_unload_entry`
- Triggers: HA unloading/reloading the entry (e.g., after options change)
- Responsibilities: Unload sensor platform, remove coordinator from `hass.data`

**Config Flow:**
- Location: `custom_components/zse_hdo/config_flow.py` — `ZSEHDOConfigFlow.async_step_user`
- Triggers: User adding the integration via UI
- Responsibilities: Fetch live HDO list, validate selection, create config entry

**Options Flow:**
- Location: `custom_components/zse_hdo/config_flow.py` — `ZSEHDOOptionsFlowHandler.async_step_init`
- Triggers: User clicking "Configure" on an existing entry
- Responsibilities: Update frequency setting, trigger full integration reload

**Sensor Platform Setup:**
- Location: `custom_components/zse_hdo/sensor.py` — `async_setup_entry`
- Triggers: HA forwarding platform setup from `__init__.py`
- Responsibilities: Instantiate all three entity objects, register with HA

## Error Handling

**Strategy:** Raise `UpdateFailed` in coordinator; HA marks entities unavailable automatically. Parser raises `aiohttp.ClientError` on network failure which is caught and re-raised as `UpdateFailed`.

**Patterns:**
- `coordinator._async_update_data` wraps all parser calls in `try/except Exception` → `raise UpdateFailed`
- `config_flow.async_step_user` catches all exceptions from parser during HDO list fetch → sets `errors["base"] = "cannot_connect"` and shows form error
- Parser `fetch_page` calls `response.raise_for_status()` to convert HTTP errors to exceptions

## Cross-Cutting Concerns

**Logging:** Module-level `_LOGGER = logging.getLogger(__name__)` in every file; DEBUG for normal flow, INFO for lifecycle events, WARNING for missing HDO, ERROR for failures.

**Validation:** `voluptuous` schema in config flow; HDO number is cast to `int` on entry creation to normalise string/int discrepancy from JSON.

**Authentication:** None — unauthenticated HTTP scraping with a browser-like User-Agent header.

---

*Architecture analysis: 2026-04-12*
