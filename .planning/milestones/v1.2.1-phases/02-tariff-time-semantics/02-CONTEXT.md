# Phase 2: Tariff Time Semantics - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Faza riesi korektne urcenie aktualnej tarify a najblizsieho prepnutia vo vsetkych casovych hranach (vratane prelomu polnoci a pracovny den/vikend), s dovrazom na timezone-aware cas v Home Assistant a odstranenie duplicity tariff/midnight logiky.

</domain>

<decisions>
## Implementation Decisions

### Time source standard
- **D-01:** Canonical source casu bude `homeassistant.util.dt` vsade (parser, sensory aj zdielane helpery), bez dalsieho miesania so `datetime.now()`.
- **D-02:** Casove intervaly zo ZSE sa interpretuju ako HA lokalny wall-clock cas a porovnavaju sa proti HA lokalnemu casu.

### Shared tariff evaluation
- **D-03:** Vznikne jedna zdielana helper vrstva/modul, ktoru budu pouzivat parser aj sensory pre vypocet tariff/midnight semantiky.
- **D-04:** Spravanie pri DST sa zamkne na HA lokalne pravidla cez `dt_util`, pri zachovani doterajsej schedule semantiky.

### Migration safety constraints
- **D-05:** Refaktor nesmie menit existujuci user-facing kontrakt entit (nazvy/atributy) ani semantiku low/high intervalov; ide o internu konsolidaciu logiky.

### Claude's Discretion
- Konkretny nazov helper modulu/symbolov a jemna interná API vrstva medzi parserom a sensory.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and acceptance boundaries
- `.planning/ROADMAP.md` — fazovy ciel, open polozky `TZ-01` a `CODE-01`, success criteria pre Phase 2.
- `.planning/REQUIREMENTS.md` — formalne requirementy `TIME-01`, `TIME-02`, `TIME-03`, `TZ-01`, `CODE-01`.
- `.planning/PROJECT.md` — projektove constraints a brownfield kontext pre stabilny refaktor.

### Existing implementation to preserve behavior
- `custom_components/zse_hdo/parser.py` — aktualny parser vypocet `current_tariff`, `is_low_tariff_now`, `last_updated`.
- `custom_components/zse_hdo/sensor.py` — aktualna runtime tariff a next-switch logika (duplicitna midnight semantika).
- `custom_components/zse_hdo/coordinator.py` — coordinator data flow a timezone utility import (`dt_util` uz pouzity pre scheduling).
- `custom_components/zse_hdo/const.py` — refresh konfiguracia a planovacie konstanty.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ZSEHDOLiveParser._parse_time` a sensor-level `_parse_time` helpery: priestor na unifikaciu cez jednu zdielanu casovu utility vrstvu.
- `homeassistant.util.dt` uz importovane v `coordinator.py`: vhodny referencny pattern pre timezone-aware pracu.

### Established Patterns
- Midnight crossing je dnes osetreny cez podmienku `end < start` v parseri aj sensoroch; refaktor musi zachovat presne rovnaku logiku vysledku.
- Sensory pocitaju tarif dynamicky pri citani stavu zo schedule (nie fetchom pri kazdom prechode), tento pattern ostava.

### Integration Points
- Parser vracia schedule payload pre coordinator; sensory cituju ten isty payload pre runtime rozhodovanie.
- Shared helper musi byt pouzitelny v parseri aj v oboch sensor branchoch bez zmeny external entity contractu.

</code_context>

<specifics>
## Specific Ideas

- Priorita je "HA time everywhere" + "single source tariff logic" bez regresie v aktualne validovanych `TIME-*` scenaroch.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-tariff-time-semantics*
*Context gathered: 2026-04-29*
