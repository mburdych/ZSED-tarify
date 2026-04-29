# Phase 4: Coordinator Reliability & Staleness - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Faza riesi reliability coordinator vrstvy pri vypadkoch zdroja a explicitne user-visible staleness informacie, bez zmeny existujuceho entity kontraktu alebo rozsirenia o novu funkcionalitu mimo `RELI-03/RELI-04`.

</domain>

<decisions>
## Implementation Decisions

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirement contracts
- `.planning/ROADMAP.md` — ciel, status a success criteria pre Phase 4 (`RELI-03`, `RELI-04` open).
- `.planning/REQUIREMENTS.md` — formalne requirementy `RELI-01..RELI-04`.
- `.planning/PROJECT.md` — brownfield constraints a stability-first prioritizacia.

### Existing implementation baseline
- `custom_components/zse_hdo/coordinator.py` — aktualny cache fallback (`_last_known_data`) a refresh scheduling flow.
- `custom_components/zse_hdo/sensor.py` — aktualny entity atributovy kontrakt, do ktoreho sa bude pridavat staleness surface.
- `custom_components/zse_hdo/const.py` — update frequency konfiguracia a konstanty.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ZSEHDOCoordinator._last_known_data` uz poskytuje fallback mechanizmus pri fetch chybe.
- Coordinator refresh lifecycle (`_async_update_data`, `_schedule_next_update`) je prirodzene miesto pre retry/backoff + stale metadata state.

### Established Patterns
- Sensory cituju data z coordinator payloadu; user-visible metadata je najbezpecnejsie pridavat ako rozsirene payload/atributy bez novych platform entit.
- Integracia preferuje stabilitu entity contractu a incremental zmeny.

### Integration Points
- Staleness metadata musi tiect z coordinatoru do entit konzistentne.
- Retry/backoff zmeny musia respektovat existujuce update frequency režimy.

</code_context>

<specifics>
## Specific Ideas

- Priorita: zachovat dostupnost entit aj pri dlhom vypadku zdroja, ale transparentne ukazat vek dat.
- Stale signal musi byt user-facing v atributech, nie iba v logoch.

</specifics>

<deferred>
## Deferred Ideas

- Samostatny dedicated staleness sensor je mimo aktualneho rozhodnutia pre tuto fazu.
- Manual acknowledgment flow po recoveri je odlozeny.
- Ostatne nevybrate gray areas (detailna retry/backoff matica, error taxonomy granularity) ostavaju na Claude discretion v scope requirements.

</deferred>

---

*Phase: 04-coordinator-reliability-staleness*
*Context gathered: 2026-04-29*
