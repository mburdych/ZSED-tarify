# Technology Stack

**Analysis Date:** 2026-04-12

## Languages

**Primary:**
- Python 3.x - All integration logic (`custom_components/zse_hdo/`)

**Secondary:**
- JSON - Translation files (`custom_components/zse_hdo/translations/en.json`, `custom_components/zse_hdo/translations/sk.json`), manifest (`custom_components/zse_hdo/manifest.json`), HACS config (`hacs.json`)

## Runtime

**Environment:**
- Home Assistant (minimum version 2024.1.0 per `hacs.json`)
- Python async runtime (asyncio) — all public methods are `async def`

**Package Manager:**
- No standalone package manager; dependency declaration is via `manifest.json` `requirements` array
- Lockfile: Not present (HA manages dependency installation)

## Frameworks

**Core:**
- Home Assistant Core — provides the full integration lifecycle, entity model, config flow, coordinator pattern
  - `homeassistant.config_entries.ConfigEntry` — config entry lifecycle (`__init__.py`)
  - `homeassistant.helpers.update_coordinator.DataUpdateCoordinator` — polling abstraction (`coordinator.py`)
  - `homeassistant.components.binary_sensor.BinarySensorEntity` — binary sensor entity (`sensor.py`)
  - `homeassistant.components.sensor.SensorEntity` — sensor entity (`sensor.py`)
  - `homeassistant.helpers.event.async_track_point_in_time` — scheduled updates (`coordinator.py`)
  - `homeassistant.helpers.aiohttp_client.async_get_clientsession` — shared HTTP session (`__init__.py`, `config_flow.py`)
  - `homeassistant.util.dt` — timezone-aware datetime utilities (`coordinator.py`)

**Config Flow:**
- `voluptuous` — schema validation for config and options forms (`config_flow.py`)
- `homeassistant.helpers.config_validation as cv` — HA-specific validators (`config_flow.py`)

**Testing:**
- None — no test framework configured; no test files present
- Standalone manual testing via `python custom_components/zse_hdo/parser.py` (runs `main()`)

**Build/Dev:**
- No build pipeline
- No linting or formatting configuration files present
- No CI/CD configuration

## Key Dependencies

**Critical:**
- `aiohttp>=3.8.0` — declared in `manifest.json` `requirements`; used for async HTTP requests to ZSE website (`parser.py`)
- `async_timeout` — used in `parser.py` for request timeouts (typically bundled with aiohttp)

**Infrastructure:**
- Home Assistant's `DataUpdateCoordinator` — manages two scheduling modes: interval (timedelta) and scheduled (point-in-time at 03:00)

## Configuration

**Environment:**
- No `.env` files; no environment variables used
- All user configuration is captured through HA's Config Flow UI (HDO number selection, update frequency)
- Config stored in HA's config entries system (`hass.data[DOMAIN][entry_id]`)

**Build:**
- `manifest.json` — integration metadata, version (`1.0.8`), requirements
- `hacs.json` — HACS marketplace metadata (country: SK, min HA: 2024.1.0)

## Platform Requirements

**Development:**
- A running Home Assistant instance with `custom_components/zse_hdo/` copied in
- Internet access to `https://www.zsdis.sk` at runtime (iot_class: `cloud_polling`)

**Production:**
- Home Assistant instance (2024.1.0+)
- Internet connectivity to `www.zsdis.sk` — integration completely depends on this external site
- No database, no local state persistence beyond HA's config entries

---

*Stack analysis: 2026-04-12*
