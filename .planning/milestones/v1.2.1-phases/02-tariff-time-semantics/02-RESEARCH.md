# Phase 2: Tariff Time Semantics - Research

**Researched:** 2026-04-29  
**Domain:** Home Assistant tariff-time evaluation semantics (timezone-aware boundary logic)  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Canonical source casu bude `homeassistant.util.dt` vsade (parser, sensory aj zdielane helpery), bez dalsieho miesania so `datetime.now()`.
- **D-02:** Casove intervaly zo ZSE sa interpretuju ako HA lokalny wall-clock cas a porovnavaju sa proti HA lokalnemu casu.
- **D-03:** Vznikne jedna zdielana helper vrstva/modul, ktoru budu pouzivat parser aj sensory pre vypocet tariff/midnight semantiky.
- **D-04:** Spravanie pri DST sa zamkne na HA lokalne pravidla cez `dt_util`, pri zachovani doterajsej schedule semantiky.
- **D-05:** Refaktor nesmie menit existujuci user-facing kontrakt entit (nazvy/atributy) ani semantiku low/high intervalov; ide o internu konsolidaciu logiky.

### Claude's Discretion
- Konkretny nazov helper modulu/symbolov a jemna interná API vrstva medzi parserom a sensory.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TIME-01 | Correct current tariff for current time/day | Shared interval evaluator with one `in_period()` rule used by parser + sensors. |
| TIME-02 | Correct next tariff switch | Shared `next_switch()` helper with explicit midnight-crossing branch behavior. |
| TIME-03 | Correct midnight + weekend/workday boundaries | One day-type selector + crossing-period normalization in helper layer. |
| TZ-01 | Use HA `dt_util` consistently | Replace all `datetime.now()` reads in parser/sensor with `dt_util.now()`. |
| CODE-01 | Single source for tariff/midnight calculus | Create one shared module and make parser/sensors consume it (no duplicated boundary logic). |
</phase_requirements>

## Project Constraints (from .cursor/rules/)

- No `.cursor/rules/` directory exists in this repository, so there are no extra project-local rule directives beyond existing planning docs. [VERIFIED: repository glob]

## Summary

Phase 2 is primarily a semantic-consolidation refactor, not a feature expansion: behavior for current tariff and next switch already works for TIME-01/02/03 in shipped code, but timezone sourcing and duplicated boundary logic remain open (`TZ-01`, `CODE-01`). [VERIFIED: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `custom_components/zse_hdo/parser.py`, `custom_components/zse_hdo/sensor.py`]

The highest-value implementation path is to centralize all tariff-time calculations into one pure helper module that takes `(schedule, now_dt)` and returns deterministic answers for: active tariff, next switch, and day-type selection. Parser and sensors should both call that module while retaining current output schema and entity attributes. [VERIFIED: locked decisions D-01..D-05 + codebase structure]

Timezone handling should use Home Assistant `dt_util.now()` and timezone-aware datetime values consistently, matching HA guidance that timestamp values should carry timezone info and are normalized in core sensor handling. [CITED: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/core/entity/sensor.md] [CITED: https://github.com/home-assistant/core/blob/dev/homeassistant/util/dt.py]

**Primary recommendation:** Implement a new shared `time_semantics` helper module (pure functions), migrate parser + sensors to it in one phase, and preserve all current entity contract fields unchanged.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Fetching ZSE schedule | API / Backend (integration runtime) | — | Happens in integration backend via parser HTTP call, not frontend. |
| Timezone-aware "now" source | API / Backend (integration runtime) | — | Tariff decisions are computed in Python integration logic. |
| Current tariff decision | API / Backend (integration runtime) | Database / Storage | Computed from in-memory schedule payload managed by coordinator. |
| Next-switch prediction | API / Backend (integration runtime) | Database / Storage | Derived from schedule + current time, no client ownership. |
| Entity presentation (attributes/state) | API / Backend (integration runtime) | Browser / Client | HA frontend only renders states; semantics belong in integration code. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `homeassistant.util.dt` | HA Core bundled | Canonical timezone-aware current time/date operations | Native HA utility, aligns with locked D-01 and HA timezone model. [CITED: https://github.com/home-assistant/core/blob/dev/homeassistant/util/dt.py] |
| `datetime` (stdlib) | Python stdlib | `time`, `timedelta`, date arithmetic | Required for interval boundaries and day offsets in helper logic. [VERIFIED: current code imports] |
| `DataUpdateCoordinator` + `CoordinatorEntity` | HA Core bundled | Shared schedule refresh + entity fan-out | Existing architecture already depends on this pattern. [VERIFIED: `custom_components/zse_hdo/coordinator.py`, `custom_components/zse_hdo/sensor.py`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `homeassistant.components.sensor` timestamp semantics | HA Core bundled | datetime-native sensor values with tzinfo | For `next_switch` datetime correctness and consistent HA formatting. [CITED: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/core/entity/sensor.md] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `dt_util.now()` | `datetime.now()` | Breaks D-01, risks naive/aware mismatches in HA timezone contexts. |
| Shared helper module | Keep duplicated code in parser/sensors | Faster short-term edits, but high regression risk and CODE-01 remains open. |

**Installation:**  
No new third-party dependencies are recommended for this phase. [VERIFIED: phase scope + current stack]

## Architecture Patterns

### System Architecture Diagram

```text
ZSE HTML
  -> parser.fetch_page()
  -> parser.normalize_schedule()
  -> shared_time_semantics.current_tariff(schedule, dt_util.now())
  -> coordinator.data cache
  -> tariff sensor is_on() -> shared_time_semantics.current_tariff(...)
  -> next-switch sensor native_value() -> shared_time_semantics.next_switch(...)
  -> today-schedule sensor -> shared_time_semantics.day_type(...)
  -> HA state machine / UI rendering
```

### Recommended Project Structure

```text
custom_components/zse_hdo/
├── parser.py                 # fetch + extract + normalize only
├── coordinator.py            # refresh/cache orchestration
├── sensor.py                 # entity presentation layer
└── time_semantics.py         # NEW: shared tariff/day/next-switch pure helpers
```

### Pattern 1: Pure time-semantics functions
**What:** Stateless helper functions operating on `(schedule, now_dt)` and returning typed results.  
**When to use:** Any current/next tariff computation in parser/sensors.  
**Example:**
```python
# Source: codebase pattern + HA dt_util docs
from homeassistant.util import dt as dt_util

def current_tariff(schedule: dict, now_dt=None) -> str:
    now_dt = now_dt or dt_util.now()
    # ... shared period evaluation ...
```

### Pattern 2: Explicit midnight-crossing branch
**What:** Treat `end < start` as period crossing midnight and evaluate with `>= start OR < end`.  
**When to use:** Every low-tariff interval check and next-switch search.  
**Example:**
```python
if end < start:
    in_period = current_time >= start or current_time < end
else:
    in_period = start <= current_time < end
```

### Anti-Patterns to Avoid
- **Mixed clock sources:** Combining `datetime.now()` and `dt_util.now()` creates timezone inconsistency under HA local timezone settings.
- **Logic fork drift:** Keeping similar boundary logic in parser and two sensor classes causes silent semantic drift over time.
- **Entity contract edits during refactor:** Renaming attributes or changing output shape violates D-05 and creates migration pain.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Timezone normalization | Custom timezone wrapper | `homeassistant.util.dt` | Already handles HA default timezone and aware datetime semantics. [CITED: https://github.com/home-assistant/core/blob/dev/homeassistant/util/dt.py] |
| Sensor datetime serialization | Manual ISO/string timezone conversion everywhere | Return timezone-aware datetime and let HA sensor core normalize | HA core enforces timestamp handling rules. [CITED: https://github.com/home-assistant/core/blob/dev/homeassistant/components/sensor/__init__.py] |

**Key insight:** keep custom code focused on tariff domain logic, not generic timezone/timestamp plumbing.

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | Config entry stores `hdo_number` and `update_frequency`; coordinator data stores schedule payload with existing keys (`workday`, `weekend`, `current_tariff`, etc.). [VERIFIED: `__init__.py`, `config_flow.py`, `coordinator.py`, `parser.py`] | Code edit only; preserve schema/keys (no data migration). |
| Live service config | Home Assistant entity registry depends on stable `unique_id` strings (`zse_hdo_<N>_*`). [VERIFIED: `sensor.py`] | Preserve IDs; no live config migration if unchanged. |
| OS-registered state | None found in repo scope for this phase (no system task/unit/process naming touched). [VERIFIED: phase scope] | None. |
| Secrets/env vars | No env-var or secret-name coupling to tariff semantics found in integration code. [VERIFIED: inspected phase files] | None. |
| Build artifacts | None (project has no package build/test artifact pipeline). [VERIFIED: `CLAUDE.md`, `AGENTS.md`] | None. |

## Common Pitfalls

### Pitfall 1: Midnight-crossing regression during consolidation
**What goes wrong:** Helper rewrite accidentally changes `23:45-05:45` inclusion logic.  
**Why it happens:** Crossing intervals use different boolean condition than same-day intervals.  
**How to avoid:** Keep one canonical predicate and reuse it everywhere.  
**Warning signs:** Current tariff flips at midnight unexpectedly for known crossing schedules.

### Pitfall 2: Weekend/day-type mismatch for "tomorrow" next switch
**What goes wrong:** Step-3 fallback ("tomorrow first period") uses today's day type.  
**Why it happens:** Implementation often reuses current day period list for tomorrow candidate. [VERIFIED: current `_get_next_switch` flow in `sensor.py`]  
**How to avoid:** Resolve day type from candidate datetime, not from `now` only.  
**Warning signs:** Friday-night or Sunday-night transitions predict wrong next period.

### Pitfall 3: Naive datetime leakage
**What goes wrong:** Mixing naive datetimes and aware datetimes creates conversion bugs or inconsistent UI timestamps.  
**Why it happens:** Direct `datetime.now()` usage in HA integration layer. [VERIFIED: parser/sensor imports and calls]  
**How to avoid:** Standardize on `dt_util.now()` and timezone-aware datetime flow.  
**Warning signs:** Tests/manual checks pass in one timezone but fail after timezone/DST change.

## Code Examples

Verified patterns from official sources:

### HA-aware now source
```python
# Source: https://github.com/home-assistant/core/blob/dev/homeassistant/util/dt.py
from homeassistant.util import dt as dt_util

now_dt = dt_util.now()
```

### Timestamp sensor requirement
```python
# Source: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/core/entity/sensor.md
# SensorDeviceClass.TIMESTAMP requires native_value to return datetime with tzinfo
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Duplicate tariff logic in multiple classes | Shared pure helper module reused by parser + sensors | Recommended in this phase | Lower regression risk, CODE-01 closure |
| `datetime.now()` in HA integration code | `dt_util.now()` unified source | Existing HA best practice (ongoing) | Better TZ/DST correctness and consistency |

**Deprecated/outdated:**
- `datetime.now()` as integration-wide canonical clock source in HA custom components for semantic logic. [CITED: https://github.com/home-assistant/core/blob/dev/homeassistant/util/dt.py]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No hidden runtime OS registrations are affected by this phase. [ASSUMED] | Runtime State Inventory | Could miss one manual post-deploy update step. |
| A2 | No external service configuration outside git encodes tariff semantic behavior. [ASSUMED] | Runtime State Inventory | Unexpected environment-specific drift during rollout. |

## Open Questions (RESOLVED)

1. **Should parser continue emitting `current_tariff` in fetched payload?** **RESOLVED**
   - Resolution: **Yes**, parser keeps emitting `current_tariff` for backward compatibility, but value is explicitly treated as derived from the shared helper semantics.
   - Rationale: This preserves existing payload contract and user automation expectations (D-05) while still consolidating logic (D-03/CODE-01).

2. **Should next-switch logic consider tomorrow day-type explicitly in fallback path?** **RESOLVED**
   - Resolution: **Yes**, fallback path must resolve day-type from the candidate datetime (including tomorrow) rather than reusing today's period set.
   - Rationale: Prevents Friday/Sunday late-night misprediction and aligns with TIME-02/TIME-03 boundary semantics.

## Environment Availability

Step 2.6: SKIPPED (no new external dependencies identified; phase is internal Python refactor within existing Home Assistant integration runtime).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None currently configured |
| Config file | none — see Wave 0 |
| Quick run command | `python custom_components/zse_hdo/parser.py` |
| Full suite command | Manual HA dev-instance smoke test (integration setup + entity checks) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TIME-01 | Correct current tariff | manual/smoke | `python custom_components/zse_hdo/parser.py` (baseline only) | ❌ Wave 0 |
| TIME-02 | Correct next switch | manual/smoke | HA dev-instance check of next-switch sensor | ❌ Wave 0 |
| TIME-03 | Midnight/weekend boundaries | manual scenario | HA dev-instance with boundary times | ❌ Wave 0 |
| TZ-01 | Consistent dt_util usage | static/code review | `rg "datetime\.now\(" custom_components/zse_hdo` | ❌ Wave 0 |
| CODE-01 | Single shared helper | static/code review | `rg "_parse_time|_calculate_current_tariff|_get_next_switch" custom_components/zse_hdo` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** targeted static checks (`rg`) + parser smoke run.
- **Per wave merge:** parser smoke run + manual HA entity verification (current tariff + next switch around boundary times).
- **Phase gate:** manual HA verification of all 5 requirements before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/` test harness (missing)
- [ ] Deterministic fixtures for midnight-crossing/day-type scenarios (missing)
- [ ] Reusable helper-level unit tests for shared time semantics module (missing)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not in phase scope |
| V3 Session Management | no | Not in phase scope |
| V4 Access Control | no | Not in phase scope |
| V5 Input Validation | yes | Keep strict time-string parsing and defensive schedule handling in shared helper |
| V6 Cryptography | no | Not in phase scope |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed interval inputs causing wrong tariff decision | Tampering | Validate period fields and fail safely to "high"/unknown instead of crashing |
| Silent logic drift after refactor | Tampering | Single helper + targeted boundary regression checks |

## Sources

### Primary (HIGH confidence)
- Repository code (`custom_components/zse_hdo/parser.py`, `sensor.py`, `coordinator.py`, `config_flow.py`, `__init__.py`) - current behavior, duplication points, and data flow.
- `.planning/phases/02-tariff-time-semantics/02-CONTEXT.md` - locked decisions and scope constraints.
- `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md` - requirement IDs, phase status, success criteria.

### Secondary (MEDIUM confidence)
- [Home Assistant sensor entity docs](https://github.com/home-assistant/developers.home-assistant/blob/master/docs/core/entity/sensor.md) - timestamp device class requirement.
- [Home Assistant `dt_util` source](https://github.com/home-assistant/core/blob/dev/homeassistant/util/dt.py) - timezone-aware `now()` behavior.
- [Home Assistant sensor core handling](https://github.com/home-assistant/core/blob/dev/homeassistant/components/sensor/__init__.py) - timestamp normalization behavior.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - uses existing in-repo + HA-native utilities; no new dependency uncertainty.
- Architecture: HIGH - directly derived from current integration layer boundaries.
- Pitfalls: MEDIUM - strongly code-grounded, but full boundary matrix still needs runtime validation.

**Research date:** 2026-04-29  
**Valid until:** 2026-05-29
