# Phase 04: coordinator-reliability-staleness - Research

**Researched:** 2026-04-29  
**Domain:** Home Assistant DataUpdateCoordinator reliability and staleness surfacing  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Degraded mode cache behavior
- **D-01:** Pri neúspešnom refreshi sa ma pouzit posledne uspesne cache data bez hard casoveho limitu (degraded rezim ostava dostupny, kym zdroj neobnovi aktualizaciu).
- **D-02:** Staleness sa ma explicitne signalizovat userovi aj pocas unlimited-cache rezimu cez stale flag + vek dat.

### User-visible staleness surface
- **D-03:** Staleness metadata sa pridaju do atributov existujucich entit (bez zavedenia noveho dedicated sensoru).
- **D-04:** Logs-only varianta nie je akceptovana; stale stav musi byt viditelny priamo v entitach.

### Recovery behavior
- **D-05:** Po prvom uspesnom refreshi sa stale flag automaticky vycisti a vek dat sa resetne bez manualneho zasahu.

### Claude's Discretion
- Presne nazvy atributov pre stale flag/vek dat a na ktorych konkretnych entitach budu exponovane.
- Presne nastavenie retry/backoff parametrov vramci Phase 4 scope, ak zachovaju D-01..D-05 a requirements `RELI-03/RELI-04`.

### Deferred Ideas (OUT OF SCOPE)
- Samostatny dedicated staleness sensor je mimo aktualneho rozhodnutia pre tuto fazu.
- Manual acknowledgment flow po recoveri je odlozeny.
- Ostatne nevybrate gray areas (detailna retry/backoff matica, error taxonomy granularity) ostavaju na Claude discretion v scope requirements.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RELI-01 | `ZSEHDOCoordinator` (`DataUpdateCoordinator`) je jediny zdroj refresh logiky a cache pre vsetky entity. [VERIFIED: `.planning/REQUIREMENTS.md`] | Keep all retry/backoff and staleness state in coordinator data payload; entities remain read-only consumers. [VERIFIED: `custom_components/zse_hdo/coordinator.py`, `custom_components/zse_hdo/sensor.py`] |
| RELI-02 | Pri docasnom vypadku zdroja integracia pouzije posledne uspesne data (`_last_known_data`). [VERIFIED: `.planning/REQUIREMENTS.md`] | Preserve unlimited cached fallback and annotate degraded mode via explicit stale metadata fields. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`, `custom_components/zse_hdo/coordinator.py`] |
| RELI-03 | Explicitny retry/backoff pri opakovanych chybach. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use `UpdateFailed(retry_after=...)` for interval polling and internal one-shot retry timer for scheduled mode, with capped exponential backoff + jitter. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/, https://developers.home-assistant.io/docs/integration_fetching_data/] |
| RELI-04 | Stav zastaranosti dat je explicitne dostupny pre uzivatela ako odlisny entity atribut/sensor (vek poslednej uspesnej aktualizacie, nielen timestamp). [VERIFIED: `.planning/REQUIREMENTS.md`] | Add staleness attributes (`is_stale`, `stale_for_s`, `last_success_at`, `last_error_at`, `consecutive_failures`) to existing entities via coordinator payload. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`, `custom_components/zse_hdo/sensor.py`] |
</phase_requirements>

## Summary

Phase 4 should keep the existing reliability baseline (single coordinator + unlimited cached fallback) and add two explicit behaviors: failure backoff control and entity-visible staleness metadata. [VERIFIED: `.planning/REQUIREMENTS.md`, `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`, `custom_components/zse_hdo/coordinator.py`]

Home Assistant now supports `UpdateFailed(retry_after=...)`, which delays the next scheduled refresh and then automatically resumes normal cadence after a successful refresh. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/] This directly matches RELI-03 for interval mode and provides clean recovery semantics for D-05. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`]

For RELI-04, the lowest-risk path is to enrich coordinator data with staleness fields and expose them through current `extra_state_attributes` in all three entities, without adding new entity types. [VERIFIED: `custom_components/zse_hdo/sensor.py`, `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`]

**Primary recommendation:** Implement a coordinator-owned reliability state machine (`last_success_at`, `consecutive_failures`, `next_retry_at`, `is_stale`) and publish that state in existing entity attributes while preserving current fallback behavior.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Retry/backoff policy | Coordinator (`DataUpdateCoordinator`) | Parser/network client exceptions | Retry decisions belong at refresh orchestration boundary, not entity layer. [VERIFIED: `custom_components/zse_hdo/coordinator.py`] |
| Cache fallback availability | Coordinator cache (`_last_known_data`) | Entity availability flags | Cache ownership already exists in coordinator and should remain single-source. [VERIFIED: `custom_components/zse_hdo/coordinator.py`, `.planning/REQUIREMENTS.md`] |
| Staleness computation (`stale_for_s`, `is_stale`) | Coordinator state | Entity attributes | Staleness depends on refresh lifecycle timestamps, which entities do not own. [VERIFIED: `custom_components/zse_hdo/coordinator.py`, `custom_components/zse_hdo/sensor.py`] |
| User-facing stale observability | Existing entity `extra_state_attributes` | Logs | D-03/D-04 require user-visible metadata on entities, not logs-only. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`] |
| Recovery reset after success | Coordinator success path | Entity render | D-05 reset naturally occurs in coordinator after successful fetch updates metadata. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`] |

## Project Constraints (from .cursor/rules/)

No `.cursor/rules/` directory exists in this repository, so no extra project-local directives were found beyond repository docs. [VERIFIED: filesystem scan]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Home Assistant `DataUpdateCoordinator` | Runtime-provided by HA Core (version follows host HA install) | Centralized refresh scheduling, error handling, listener updates | Official HA integration pattern for coordinated polling and failure handling. [CITED: https://developers.home-assistant.io/docs/integration_fetching_data/] |
| Home Assistant `UpdateFailed(retry_after=...)` | Available in HA Core after 2025-11 feature release | Native backoff hint to coordinator scheduler | Built-in retry delay semantics and automatic cadence recovery reduce custom timer code. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `homeassistant.util.dt` | Runtime-provided by HA Core | TZ-aware now/timestamp handling for staleness age | Use for all staleness timestamps and age math in coordinator/entity metadata. [VERIFIED: `custom_components/zse_hdo/coordinator.py`, `custom_components/zse_hdo/sensor.py`] |
| Python stdlib (`datetime`) | Python 3.14.3 in local dev shell | Duration arithmetic and ISO serialization | Use only behind HA `dt_util` wall-clock sources for consistency. [VERIFIED: local shell `python --version`] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `UpdateFailed(retry_after=...)` | Custom `async_track_point_in_time` retry pipeline for interval mode | Reinvents coordinator scheduling behavior and increases edge-case burden. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/] |
| Entity attribute staleness fields | Dedicated new stale sensor entity | Conflicts with locked D-03 scope for this phase. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`] |

**Installation:** No new third-party package required for Phase 4. [VERIFIED: phase scope + current imports]

**Version verification:** N/A for new packages (none introduced). HA API features verified against official HA developer docs/blog pages fetched on 2026-04-29. [CITED: https://developers.home-assistant.io/docs/integration_fetching_data/, https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/]

## Architecture Patterns

### System Architecture Diagram

```text
Scheduled/interval refresh trigger
            |
            v
ZSEHDOCoordinator._async_update_data()
            |
            +--> parser.get_schedule() success
            |         |
            |         v
            |   update reliability metadata:
            |   last_success_at, failures=0, is_stale=false
            |         |
            |         v
            |   publish fresh payload -> entities render attrs
            |
            +--> parser/get_schedule error
                      |
                      +--> if cached data exists:
                      |      compute stale_for_s + failures + retry plan
                      |      return enriched cached payload (degraded mode)
                      |
                      +--> if no cache:
                             raise UpdateFailed (setup or runtime)
```

### Recommended Project Structure
```text
custom_components/zse_hdo/
├── coordinator.py    # retry/backoff policy + staleness metadata state machine
├── sensor.py         # surface staleness attributes on existing entities
└── const.py          # optional reliability tunables (min/max retry, jitter cap)
```

### Pattern 1: Coordinator-owned reliability metadata envelope
**What:** Always return coordinator payload in a stable envelope containing schedule data plus reliability metadata keys (`reliability`).  
**When to use:** Every successful or degraded refresh so entities expose consistent attributes. [VERIFIED: `custom_components/zse_hdo/sensor.py`]

**Example:**
```python
payload = {
    **schedule,
    "reliability": {
        "is_stale": False,
        "stale_for_s": 0,
        "last_success_at": dt_util.now().isoformat(),
        "last_error_at": None,
        "consecutive_failures": 0,
    },
}
```
Source pattern: coordinator pre-processing before entity consumption. [CITED: https://developers.home-assistant.io/docs/integration_fetching_data/]

### Pattern 2: Explicit backoff via `UpdateFailed(retry_after=...)`
**What:** Raise `UpdateFailed` with computed retry seconds for repeated transient failures (especially rate-limits).  
**When to use:** Interval-based polling after first successful setup refresh. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/]

**Example:**
```python
except ApiRateLimitedError as err:
    delay = min(max(err.retry_after_seconds, 30), 1800)
    raise UpdateFailed(f"Rate limited: {err}", retry_after=delay) from err
```
Source pattern: official HA retry-after guidance. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/]

### Pattern 3: Scheduled-mode one-shot retry lane
**What:** For `1day/1week/1month` mode (`update_interval=None`), schedule an internal short retry timer when refresh fails, while preserving the next long cadence anchor.  
**When to use:** Current integration defaults to weekly scheduled updates, so no built-in interval scheduler exists to consume `retry_after`. [VERIFIED: `custom_components/zse_hdo/coordinator.py`, `custom_components/zse_hdo/const.py`]

**Example:**
```python
if self.frequency_type == "scheduled" and failed:
    retry_at = dt_util.now() + timedelta(seconds=retry_delay_s)
    self._schedule_retry_once(retry_at)
```
Source: local architecture adaptation to existing scheduled mode. [VERIFIED: `custom_components/zse_hdo/coordinator.py`] [ASSUMED]

### Anti-Patterns to Avoid
- **Backoff only in logs:** Violates D-04 because users cannot see stale state from entities. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`]
- **Entity-local staleness timers:** Duplicates logic across entities and risks drift; keep single source in coordinator. [VERIFIED: `custom_components/zse_hdo/sensor.py`]
- **Infinite aggressive retries:** Can overload source endpoint and violate RELI-03 intent. [VERIFIED: `.planning/REQUIREMENTS.md`] [ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Interval backoff scheduling | Custom loop/call_at retry queue for interval mode | `UpdateFailed(retry_after=...)` | HA coordinator already integrates this into next refresh scheduling and resets on recovery. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/] |
| Entity subscription fan-out | Manual observer/event bus in integration | `CoordinatorEntity` + coordinator listener updates | Standard HA coordinator pattern; less state-sync risk. [CITED: https://developers.home-assistant.io/docs/integration_fetching_data/] |
| Error-state availability toggles per entity | Ad-hoc available/unavailable forcing in each entity | Coordinator `last_update_success` + stale metadata attrs | Keeps entities available with cached data while still signaling degradation. [VERIFIED: `custom_components/zse_hdo/coordinator.py`, `custom_components/zse_hdo/sensor.py`] |

**Key insight:** Reliability here is mostly orchestration correctness, not new parsing logic; leverage coordinator-native mechanisms and only add minimal state metadata.

## Common Pitfalls

### Pitfall 1: Assuming `retry_after` works during first refresh
**What goes wrong:** Backoff value is ignored during setup and integration still raises `ConfigEntryNotReady`. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/]  
**Why it happens:** HA only honors `retry_after` after config entry setup succeeds. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/]  
**How to avoid:** Keep first-refresh behavior unchanged; apply retry policy only for runtime refreshes after successful setup. [VERIFIED: `custom_components/zse_hdo/coordinator.py`]  
**Warning signs:** Repeated setup retries despite custom runtime backoff logic.

### Pitfall 2: Scheduled mode without retry lane
**What goes wrong:** With weekly default schedule, a failure may wait until next week if no explicit short retry is added. [VERIFIED: `custom_components/zse_hdo/const.py`, `custom_components/zse_hdo/coordinator.py`]  
**Why it happens:** Scheduled mode uses `async_track_point_in_time` and `update_interval=None`. [VERIFIED: `custom_components/zse_hdo/coordinator.py`]  
**How to avoid:** Add one-shot scheduled retry after failure and clear it on next success. [ASSUMED]  
**Warning signs:** `consecutive_failures > 0` persists for days while endpoint recovered.

### Pitfall 3: Stale metadata not reset on recovery
**What goes wrong:** Entities keep `is_stale=true` or stale age even after successful refresh. [ASSUMED]  
**Why it happens:** Recovery path updates schedule but not reliability fields. [ASSUMED]  
**How to avoid:** In success path, atomically reset stale fields (`is_stale=false`, `stale_for_s=0`, `consecutive_failures=0`, clear `last_error_at`). [VERIFIED: D-05 in `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`]  
**Warning signs:** `last_success_at` newer than `last_error_at` while `is_stale=true`.

## Code Examples

Verified patterns from official/local sources:

### Official coordinator update pattern
```python
try:
    async with async_timeout.timeout(10):
        return await self.my_api.fetch_data(listening_idx)
except ApiError as err:
    raise UpdateFailed(f"Error communicating with API: {err}")
except ApiRateLimited as err:
    raise UpdateFailed(retry_after=60)
```
Source: [HA fetching data docs](https://developers.home-assistant.io/docs/integration_fetching_data/).

### Current local fallback baseline
```python
except Exception as err:
    _LOGGER.error(f"Error fetching HDO data for {self.hdo_number}: {err}")

    if self._last_known_data is not None:
        _LOGGER.warning(
            f"HDO {self.hdo_number}: using cached schedule due to fetch error"
        )
        return self._last_known_data
```
Source: `custom_components/zse_hdo/coordinator.py` (existing RELI-02 behavior).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Generic `UpdateFailed`/default cadence only | `UpdateFailed(retry_after=...)` supported by HA coordinator | 2025-11-17 | Integrations can honor API backoff hints without custom scheduler for interval polling. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/] |

**Deprecated/outdated:**
- Treating repeated runtime failures with only fixed base polling interval is now suboptimal where backoff hints exist. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Scheduled-mode failures should use a custom one-shot retry timer because `retry_after` primarily affects interval scheduling path. | Architecture Patterns / Pitfalls | Medium - planner may choose suboptimal retry implementation for scheduled frequencies. |
| A2 | Recommended backoff bounds for this integration can default to ~30s min and ~1800s max without harming UX. | Pattern 2 | Low-Medium - may need tuning based on real endpoint behavior. |
| A3 | Not resetting stale metadata atomically on success is a likely regression risk. | Pitfalls | Low - easy to verify in implementation tests. |

## Open Questions (RESOLVED)

1. **Should stale metadata be namespaced (`reliability.*`) or flat top-level entity attributes? — RESOLVED**
   - Decision: Use flat top-level entity attributes (`is_stale`, `stale_for_s`, `consecutive_failures`, `last_success_at`, `last_error_at`, `next_retry_at`) while coordinator internals may remain namespaced.
   - Rationale: Existing sensor attributes are flat, and D-03/D-04 require immediate user-visible ergonomics in existing entities. [VERIFIED: `custom_components/zse_hdo/sensor.py`, `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`]

2. **What retry sequence should be locked for scheduled mode? — RESOLVED**
   - Decision: Lock capped exponential progression for scheduled-mode retry lane: 5m -> 15m -> 30m -> 60m -> 6h cap, reset to base after first successful refresh.
   - Rationale: Weekly default cadence makes missing retry lane operationally risky, and this sequence balances recovery speed against source protection under RELI-03.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python runtime | Running local checks/tests | ✓ | 3.14.3 | — |
| pip | Installing test tooling | ✓ | 26.0.1 | — |
| pytest CLI | Validation Architecture commands | ✗ (not on PATH) | — | Use `python -m pytest` after installing pytest package |
| Home Assistant runtime | True integration runtime verification | ✗ (not detected in this repo shell) | — | Manual dev-instance validation per `CLAUDE.md` |

**Missing dependencies with no fallback:**
- None blocking planning; runtime validation will require a Home Assistant dev instance for full E2E confirmation. [VERIFIED: `CLAUDE.md`]

**Missing dependencies with fallback:**
- `pytest` command not installed globally; use `python -m pip install pytest pytest-asyncio` then invoke `python -m pytest ...`. [VERIFIED: local shell checks]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (+ pytest-asyncio) [VERIFIED: `pytest.ini`, existing tests layout] |
| Config file | `pytest.ini` |
| Quick run command | `python -m pytest tests/test_parser_get_schedule.py -q -x` |
| Full suite command | `python -m pytest tests -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RELI-01 | Coordinator remains single source for refresh/cache/reliability metadata | unit | `python -m pytest tests/test_coordinator_reliability.py::test_coordinator_payload_owner -q -x` | ❌ Wave 0 |
| RELI-02 | On refresh error with cache, returns cached payload with stale metadata | unit | `python -m pytest tests/test_coordinator_reliability.py::test_cached_fallback_marks_stale -q -x` | ❌ Wave 0 |
| RELI-03 | Repeated errors trigger explicit backoff policy | unit | `python -m pytest tests/test_coordinator_reliability.py::test_backoff_progression -q -x` | ❌ Wave 0 |
| RELI-04 | Existing entities expose stale age/flags via attributes | unit | `python -m pytest tests/test_sensor_staleness_attrs.py -q -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_coordinator_reliability.py -q -x`
- **Per wave merge:** `python -m pytest tests -q`
- **Phase gate:** Full suite green + manual HA smoke check for entity attributes.

### Wave 0 Gaps
- [ ] `tests/test_coordinator_reliability.py` — coordinator retry/backoff/staleness state tests.
- [ ] `tests/test_sensor_staleness_attrs.py` — entity attribute surfacing tests.
- [ ] Optional helper fixture for synthetic coordinator payload with reliability metadata.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase does not introduce auth flow. [VERIFIED: phase scope] |
| V3 Session Management | no | No session layer changes in this phase. [VERIFIED: phase scope] |
| V4 Access Control | no | No ACL/permission model changes. [VERIFIED: phase scope] |
| V5 Input Validation | yes | Sanitize retry values (API `Retry-After` or computed delays) to bounded numeric range before applying. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/] |
| V6 Cryptography | no | No crypto primitives in scope. [VERIFIED: phase scope] |

### Known Threat Patterns for coordinator reliability stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Retry storm against source endpoint | Denial of Service | Capped exponential backoff + jitter; honor provider backoff hints when available. [CITED: https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/] [ASSUMED] |
| Silent stale-data serving | Integrity | Explicit stale metadata on entities (`is_stale`, age) and warning logs on fallback path. [VERIFIED: D-02/D-04 in `04-CONTEXT.md`] |
| Unbounded stale duration without visibility | Availability/Integrity | Keep unlimited cache per D-01 but surface `stale_for_s` and failure counters for operator awareness. [VERIFIED: `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md`] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/04-coordinator-reliability-staleness/04-CONTEXT.md` - locked decisions and scope boundaries.
- `.planning/REQUIREMENTS.md` - RELI requirement contracts.
- `.planning/ROADMAP.md` - phase goal and success criteria.
- `custom_components/zse_hdo/coordinator.py` - current refresh/cached fallback behavior.
- `custom_components/zse_hdo/sensor.py` - current entity attribute surfaces.
- `custom_components/zse_hdo/const.py` - update frequencies and scheduled mode defaults.
- [HA fetching data docs](https://developers.home-assistant.io/docs/integration_fetching_data/) - official coordinator integration patterns.
- [HA retry-after blog](https://developers.home-assistant.io/blog/2025/11/17/retry-after-update-failed/) - official retry/backoff semantics and setup caveat.

### Secondary (MEDIUM confidence)
- [HA DataUpdateCoordinator source (dev branch)](https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/update_coordinator.py) - implementation confirmation of `_retry_after` scheduling/reset behavior.

### Tertiary (LOW confidence)
- None beyond explicitly tagged `[ASSUMED]` recommendations.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - based on official HA docs and current coordinator implementation.
- Architecture: HIGH - directly derived from local code structure and locked decisions.
- Pitfalls: MEDIUM - mostly verified; some operational tuning guidance is assumed.

**Research date:** 2026-04-29  
**Valid until:** 2026-05-29
