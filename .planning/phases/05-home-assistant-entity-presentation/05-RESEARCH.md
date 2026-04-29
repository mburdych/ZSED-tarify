# Phase 5: home-assistant-entity-presentation - Research

**Researched:** 2026-04-29  
**Domain:** Home Assistant entity contract hardening (retroactive)  
**Confidence:** HIGH

## User Constraints (from CONTEXT.md)

### Locked Decisions
No `*-CONTEXT.md` exists for this phase. [VERIFIED: local repo scan]

### Claude's Discretion
Research and recommend retro-hardening steps for already-validated entity presentation behavior (contract stability, docs/examples parity, dashboard compatibility baseline). [VERIFIED: user objective + additional context]

### Deferred Ideas (OUT OF SCOPE)
No deferred ideas were provided via `CONTEXT.md`. [VERIFIED: local repo scan]

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HAPR-01 | Integracia poskytne 3 entity: binary_sensor aktualnej tarify, sensor najblizsieho prechodu, sensor denneho rozpisu. | Freeze the 3-entity surface and test for exact entity IDs and domains. [VERIFIED: `.planning/REQUIREMENTS.md`, `custom_components/zse_hdo/sensor.py`] |
| HAPR-02 | Entity maju stabilne unique_id, zrozumitelne atributy a metadata vhodne pre dashboard pouzitie. | Add explicit "entity contract" tests for unique IDs + required attributes including reliability metadata. [VERIFIED: `sensor.py`, `tests/test_sensor_staleness_attrs.py`] |
| HAPR-03 | Dashboard prezentacia je prehladna pre bezne komunitne pouzitie (entities card + Mushroom/card-mod recepty). | Keep README/EXAMPLES examples aligned to live attributes and publish compatibility baseline for core Entities card + optional Mushroom/card-mod. [VERIFIED: `README.md`, `EXAMPLES.md`] |

## Summary

Phase 5 is functionally shipped, so planning should target **retroactive hardening of contracts**, not feature expansion. The current integration already exposes exactly three entities and stable unique IDs (`zse_hdo_<n>_*`), and already projects reliability metadata into attributes. [VERIFIED: `custom_components/zse_hdo/sensor.py`, `.planning/REQUIREMENTS.md`]

The highest-value planning target is to formalize what is already "implicitly stable" into explicit contracts: entity IDs, unique IDs, required attributes, and docs/example parity. This reduces breakage risk for dashboards and automations after future reliability or time-semantics updates. [VERIFIED: `README.md`, `EXAMPLES.md`, `tests/test_sensor_staleness_attrs.py`]

For dashboard compatibility, the baseline should be split into: (1) HA-native Entities card using entity state/attributes and (2) optional custom-card path (Mushroom + card-mod) treated as additive, not required for correctness. [CITED: https://www.home-assistant.io/lovelace/entities/, https://github.com/piitaya/lovelace-mushroom/]

**Primary recommendation:** Plan this phase as a contract-hardening wave: codify entity schema + example parity tests + compatibility matrix, with no behavioral redesign. [VERIFIED: phase context + shipped code]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Compute current tariff state | API / Backend | — | Entity state is produced in integration Python (`is_on`/`native_value`), not in dashboard YAML. [VERIFIED: `sensor.py`] |
| Expose reliability metadata (`is_stale`, etc.) | API / Backend | Frontend | Coordinator/sensors publish attributes; UI only reads/render them. [VERIFIED: `coordinator.py`, `sensor.py`] |
| Keep entity IDs/unique IDs stable | API / Backend | Database / Storage | HA entity registry keys off integration domain + platform + unique_id. [CITED: https://developers.home-assistant.io/docs/entity_registry_index/] |
| Render default dashboard view | Browser / Client | — | Lovelace Entities card consumes entity state and attributes at display time. [CITED: https://www.home-assistant.io/lovelace/entities/] |
| Render advanced timeline card | Browser / Client | API / Backend | Mushroom/card-mod templates consume `state_attr()` from exposed attributes. [CITED: https://www.home-assistant.io/template-functions/state_attr/, https://github.com/piitaya/lovelace-mushroom/] |

## Project Constraints (from .cursor/rules/)

No `.cursor/rules/` directory exists in this repository, so there are no additional project-local rule files to enforce beyond repository docs (`CLAUDE.md`, `AGENTS.md`). [VERIFIED: local repo scan]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Home Assistant Entity APIs (`SensorEntity`, `BinarySensorEntity`, `CoordinatorEntity`) | Runtime-provided by user HA install | Entity contract and update lifecycle | Official HA integration pattern for stable state/attribute presentation. [CITED: https://developers.home-assistant.io/docs/core/entity/sensor, https://developers.home-assistant.io/docs/integration_fetching_data/] |
| Home Assistant `DataUpdateCoordinator` | Runtime-provided by user HA install | Single-source coordinated polling/cache semantics | Avoids per-entity polling and centralizes refresh reliability metadata. [CITED: https://developers.home-assistant.io/docs/integration_fetching_data/] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `aiohttp` | `>=3.8.0` required by integration; latest seen `3.13.5` (2026-03-31) | HTTP fetch in parser/coordinator path | Keep manifest minimum compatible with HA runtime, validate practical compatibility in tests. [VERIFIED: `manifest.json`; CITED: https://pypi.org/project/aiohttp/] |
| Lovelace Entities card | HA built-in | Baseline dashboard compatibility target | Always include as no-extra-dependency baseline for HAPR-03. [CITED: https://www.home-assistant.io/lovelace/entities/] |
| Mushroom cards + card-mod | Community frontend add-ons | Advanced visual recipes in docs | Treat as optional enhancement path only. [CITED: https://github.com/piitaya/lovelace-mushroom/] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Contract tests for existing entities | Ad-hoc manual dashboard checks | Faster short-term, but regressions slip through during metadata changes. [VERIFIED: current docs-heavy usage] |
| Attribute-based dashboard recipes | Custom frontend card maintained in repo | More control, but much higher long-term maintenance and release burden. [ASSUMED] |

**Installation:**
```bash
py -m pytest -q tests
```

## Architecture Patterns

### System Architecture Diagram

```text
ZSE source page --> Parser normalization --> Coordinator refresh/cache/retry --> Entity state+attributes --> Lovelace dashboards
                                                     |                                   |
                                                     +--> stale/retry metadata ----------+
```

### Recommended Project Structure
```text
custom_components/zse_hdo/
├── coordinator.py      # refresh/retry/staleness source of truth
├── sensor.py           # entity contract surface (3 entities + attrs)
└── time_semantics.py   # tariff/next-switch calculations consumed by entities

tests/
├── test_sensor_staleness_attrs.py      # entity metadata contract tests
├── test_coordinator_reliability.py     # coordinator reliability contract tests
└── test_entity_presentation_contract.py # (to add) stable IDs + required attrs + docs parity
```

### Pattern 1: Contract-First Entity Surface
**What:** Define a fixed required attribute set per entity and enforce via tests.  
**When to use:** Any update that touches `sensor.py`, `coordinator.py`, docs, or examples.

**Example:**
```python
# Source: https://developers.home-assistant.io/docs/core/entity/sensor
required = {"is_stale", "stale_for_s", "consecutive_failures"}
attrs = entity.extra_state_attributes
assert required.issubset(attrs.keys())
```

### Pattern 2: Coordinator-Owned Reliability Metadata
**What:** Keep stale/retry/failure fields produced by coordinator and projected uniformly by entities.  
**When to use:** Any reliability hardening that adds/removes metadata.

**Example:**
```python
# Source: https://developers.home-assistant.io/docs/integration_fetching_data/
payload["is_stale"] = is_stale
payload["next_retry_at"] = self._next_retry_at.isoformat() if self._next_retry_at else None
```

### Anti-Patterns to Avoid
- **Dashboard-led schema drift:** Changing entity attributes to satisfy one card recipe; preserve integration contract first. [VERIFIED: phase scope]
- **Undocumented attribute churn:** Adding/removing attributes without README/EXAMPLES update and contract tests. [VERIFIED: retro-hardening objective]
- **Custom-card-only validation:** Declaring compatibility from Mushroom/card-mod only; maintain built-in Entities card baseline. [CITED: https://www.home-assistant.io/lovelace/entities/]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Entity identity persistence | Custom ID registry | HA entity registry + `unique_id` | Registry already guarantees stable mapping and user overrides. [CITED: https://developers.home-assistant.io/docs/entity_registry_index/] |
| Poll fanout per entity | Per-entity network fetch | `DataUpdateCoordinator` + `CoordinatorEntity` | Official scalable pattern, reduces redundant IO and state churn. [CITED: https://developers.home-assistant.io/docs/integration_fetching_data/] |
| Dashboard rendering engine | Bespoke frontend bundle | Native Entities card + optional Mushroom/card-mod recipes | Lower maintenance and easier user adoption. [CITED: https://www.home-assistant.io/lovelace/entities/, https://github.com/piitaya/lovelace-mushroom/] |

**Key insight:** This phase should harden contracts around proven HA primitives, not introduce new presentation architecture. [VERIFIED: roadmap + phase status]

## Common Pitfalls

### Pitfall 1: Unique ID or object-ID drift
**What goes wrong:** Existing dashboards/automations lose bindings after refactors.  
**Why it happens:** Renaming patterns without explicit compatibility gate.  
**How to avoid:** Freeze `zse_hdo_<n>_tariff|next_switch|today_schedule` patterns in tests and release checklist. [VERIFIED: `sensor.py`]  
**Warning signs:** New entity IDs appear after reload for same config entry.

### Pitfall 2: Docs/examples lag behind live attributes
**What goes wrong:** YAML templates fail (`None`/missing attr) in user dashboards.  
**Why it happens:** Attribute contract evolves without synced docs and examples.  
**How to avoid:** Add "docs parity" test that validates README/EXAMPLES referenced attrs exist in live entity payload shape. [VERIFIED: docs + tests present]  
**Warning signs:** Support reports around `state_attr(...)=None` for documented keys.

### Pitfall 3: Over-coupling to optional custom cards
**What goes wrong:** Users without HACS addons see broken guidance.  
**Why it happens:** Advanced recipes become the implied default path.  
**How to avoid:** Keep a first-class core Entities card baseline and mark Mushroom/card-mod explicitly optional. [CITED: https://www.home-assistant.io/lovelace/entities/, https://github.com/piitaya/lovelace-mushroom/]  
**Warning signs:** Docs assume `custom:*` cards before showing built-in card.

## Code Examples

Verified patterns from official sources:

### Coordinator-backed entity update flow
```python
# Source: https://developers.home-assistant.io/docs/integration_fetching_data/
class MyEntity(CoordinatorEntity, LightEntity):
    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data[self.idx]["state"]
        self.async_write_ha_state()
```

### Dashboard attribute consumption with fallback
```jinja
{# Source: https://www.home-assistant.io/template-functions/state_attr/ #}
{{ state_attr("sensor.zse_hdo_145_next_switch", "time") | default("N/A") }}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| "Functional entities are enough" | "Entities + explicit reliability metadata contract" | v1.1.0 phase hardening timeframe | Better degraded-mode observability for dashboards/automations. [VERIFIED: `README.md`, `coordinator.py`, `sensor.py`] |
| Implicit docs consistency | Versioned contract + parity checks | Recommended for this retro-hardening phase | Lower regression/support cost. [ASSUMED] |

**Deprecated/outdated:**
- Relying on manual-only dashboard checks as the primary guardrail for entity schema stability. [ASSUMED]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Building a custom frontend card would add significant maintenance burden vs docs recipes. | Alternatives Considered | Could underestimate value of bespoke UI if team wants long-term frontend ownership. |
| A2 | Current repo lacks docs-parity tests and needs a dedicated parity gate. | Common Pitfalls | If parity guard already exists elsewhere, planning may duplicate work. |

## Open Questions (RESOLVED)

1. **How strict should docs-parity checks be?**
   - Resolution: Use required-minimum contract matching (not strict exact-list snapshot matching) so additive attributes remain non-breaking.
   - Applied in planning: `05-01-PLAN.md` Task 2 and `05-02-PLAN.md` Task 1 explicitly require required-minimum parity assertions.

2. **Do we freeze Slovak user-facing attribute labels fully?**
   - Resolution: Freeze attribute keys and entity IDs as the hard compatibility contract; user-facing Slovak wording remains editable but must be release-note gated.
   - Applied in planning: `05-01-PLAN.md` enforces key/ID stability and `05-02-PLAN.md` aligns README/EXAMPLES text with contract keys.

## Environment Availability

Step 2.6: SKIPPED (no new external runtime dependencies identified for this retro-hardening phase; scope is contract/tests/docs around existing integration surface). [VERIFIED: phase objective + repo stack]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` (async mode enabled) [VERIFIED: `pytest.ini`] |
| Config file | `pytest.ini` |
| Quick run command | `py -m pytest -q tests/test_sensor_staleness_attrs.py` |
| Full suite command | `py -m pytest -q tests` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HAPR-01 | Exactly 3 expected entities remain exposed | unit/contract | `py -m pytest -q tests/test_entity_presentation_contract.py::test_three_entities_surface` | ❌ Wave 0 |
| HAPR-02 | unique_id patterns + required attrs are stable | unit/contract | `py -m pytest -q tests/test_entity_presentation_contract.py::test_unique_id_and_attrs_contract` | ❌ Wave 0 |
| HAPR-03 | docs/examples referenced attrs resolve from live payload shape | unit/docs-contract | `py -m pytest -q tests/test_entity_presentation_contract.py::test_docs_examples_attribute_parity` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `py -m pytest -q tests/test_sensor_staleness_attrs.py`
- **Per wave merge:** `py -m pytest -q tests`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_entity_presentation_contract.py` - dedicated HAPR contract + docs parity checks
- [ ] Fixture/helper for expected entity schema snapshots (can live in same file initially)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A (phase scope is presentation contract hardening) [VERIFIED: phase scope] |
| V3 Session Management | no | N/A [VERIFIED: phase scope] |
| V4 Access Control | no | N/A [VERIFIED: phase scope] |
| V5 Input Validation | yes | Validate attribute schema/keys in tests to prevent unsafe template assumptions. [ASSUMED] |
| V6 Cryptography | no | N/A (no crypto changes in scope) [VERIFIED: phase scope] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Silent contract break in entity attributes | Tampering | Contract tests + release docs parity gate before version bump. [VERIFIED: recommended hardening strategy] |
| Stale-data misinterpretation in automations | Integrity | Keep reliability attrs (`is_stale`, `stale_for_s`) consistently present across entities. [VERIFIED: `sensor.py`, `tests/test_sensor_staleness_attrs.py`] |

## Sources

### Primary (HIGH confidence)
- https://developers.home-assistant.io/docs/core/entity/sensor - sensor entity contract (`native_value`, properties from memory)
- https://developers.home-assistant.io/docs/integration_fetching_data/ - coordinator + coordinator-entity best practices
- https://developers.home-assistant.io/docs/entity_registry_index/ - unique_id and registry behavior
- https://www.home-assistant.io/lovelace/entities/ - baseline dashboard entities-card behavior
- Repository sources: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `custom_components/zse_hdo/sensor.py`, `custom_components/zse_hdo/coordinator.py`, `README.md`, `EXAMPLES.md`, `tests/test_sensor_staleness_attrs.py`, `tests/test_coordinator_reliability.py`

### Secondary (MEDIUM confidence)
- https://www.home-assistant.io/template-functions/state_attr/ - attribute retrieval/fallback behavior in templates
- https://github.com/piitaya/lovelace-mushroom/ - optional custom-card compatibility path

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - grounded in official HA docs + current repo implementation
- Architecture: HIGH - directly derived from existing coordinator/entity layering
- Pitfalls: MEDIUM - partially inferred from common integration maintenance patterns

**Research date:** 2026-04-29  
**Valid until:** 2026-05-29
