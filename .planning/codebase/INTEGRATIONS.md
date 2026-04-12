# External Integrations

**Analysis Date:** 2026-04-12

## APIs & External Services

**Slovak Electricity Distribution (ZSE/ZSD):**
- ZSD (Západoslovenská distribučná) HDO schedule page — provides the sole data source for all entities
  - URL: `https://www.zsdis.sk/Uvod/Online-sluzby/Casy-prepinania-nizkej-a-vysokej-tarify`
  - Defined in: `custom_components/zse_hdo/parser.py` as `ZSE_HDO_URL`
  - Protocol: HTTPS GET, no API key, no authentication
  - Response type: HTML page with embedded JavaScript arrays (`var household_rates = [...]`, `var business_rates = [...]`)
  - Parsing strategy: Bracket-counting extraction + JS-to-JSON conversion (regex), implemented in `ZSEHDOLiveParser._extract_javascript_array()`
  - Request timeout: 30 seconds (`REQUEST_TIMEOUT` in `parser.py`)
  - Headers sent: User-Agent mimicking a browser, Accept-Language `sk,en`

## Data Storage

**Databases:**
- None — no database used

**In-memory state:**
- Coordinator data held in `hass.data[DOMAIN][entry_id]["coordinator"].data` (a Python dict)
- Data includes: `hdo_number`, `name`, `category`, `rate_type`, `current_tariff`, `workday` periods, `weekend` periods, `last_updated`, `source`

**File Storage:**
- Local filesystem only — integration files in `custom_components/zse_hdo/`
- No file-based caching of fetched data

**Caching:**
- None — each coordinator refresh triggers a fresh HTTP fetch from ZSE

## Authentication & Identity

**Auth Provider:**
- None — ZSE website is publicly accessible, no authentication required
- No API keys, tokens, or credentials of any kind

## Monitoring & Observability

**Error Tracking:**
- None — no external error tracking service

**Logs:**
- Python standard `logging` module via `_LOGGER = logging.getLogger(__name__)` in every module
- Log levels used: `DEBUG` (fetch details, parse counts), `INFO` (setup, scheduling), `WARNING` (HDO not found, missing JS variable), `ERROR` (fetch failures, JSON parse failures)
- Errors surfaced to HA as `UpdateFailed` exceptions from `ZSEHDOCoordinator._async_update_data()` (`coordinator.py`)

## CI/CD & Deployment

**Hosting:**
- Self-hosted within a Home Assistant instance
- HACS (Home Assistant Community Store) marketplace distribution

**CI Pipeline:**
- None — no CI/CD configuration present

**Release process:**
- Manual: bump `version` in `custom_components/zse_hdo/manifest.json`, push to GitHub
- HACS picks up new releases from GitHub repository tags

## Environment Configuration

**Required env vars:**
- None

**Secrets location:**
- None — no secrets required for this integration

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None — integration is pull-only (polls ZSE website on a configurable schedule)

## Update Scheduling

**Configurable frequencies** (defined in `custom_components/zse_hdo/const.py` `UPDATE_FREQUENCIES`):

| Key | Label | Type | Interval |
|-----|-------|------|----------|
| `5min` | Every 5 minutes | interval | 300s |
| `1hour` | Every hour | interval | 3600s |
| `1day` | Once daily | scheduled | 03:00 daily |
| `1week` | Once weekly | scheduled | Monday 03:00 |
| `1month` | Once monthly | scheduled | 1st of month 03:00 |

- Default: `1week`
- Interval type: uses `DataUpdateCoordinator.update_interval` (timedelta)
- Scheduled type: uses `async_track_point_in_time` with recursive rescheduling after each fire (`coordinator.py`)

## Supported HDO Codes

- 44 codes total: 32 household categories, 12 business categories
- Retrieved live from ZSE page at config-flow time (not hardcoded)
- Examples: household 145, 146; business 101, 102
- Fetched via `ZSEHDOLiveParser.get_all_hdo_numbers()` in `config_flow.py`

---

*Integration audit: 2026-04-12*
