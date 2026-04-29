# Phase 3: Parser Verification Fixtures - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Faza zavadza opakovatelne fixture testy parser vrstvy pre requirement `PARS-04`, aby sa regresia parsera odhalila pred nasadenim. Scope je parser verification; nie plny Home Assistant test harness.

</domain>

<decisions>
## Implementation Decisions

### Test runner and scope
- **D-01:** Baseline test stack pre Phase 3 bude minimalny `pytest + pytest-asyncio`.
- **D-02:** V tejto faze sa testuje parser layer, bez `pytest-homeassistant-custom-component` harnessu.
- **D-03:** Parser testy budu bez siete, cisto z lokalnych HTML fixtures (deterministicke vstupy).

### Definition of done for PARS-04
- **D-04:** Minimum pre splnenie `PARS-04` su klucove fixture pripady + fail pri regresii parser output shape.
- **D-05:** Sirenie na rozsiahlu corner-case maticu je mozne neskor, ale nie je podmienkou tejto fazy.

### Claude's Discretion
- Presny naming test suborov, fixture suborov a helper funkcii.
- Presne rozdelenie klucovych fixture pripadov do konkretnej test modulovej struktury.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` — fazovy ciel a success criteria pre Phase 3 (`PARS-04`).
- `.planning/REQUIREMENTS.md` — formalna definicia `PARS-04`.
- `.planning/PROJECT.md` — brownfield constraints, release stabilita a parser-first priorita.

### Existing implementation and testing baseline
- `custom_components/zse_hdo/parser.py` — parser API surface a behavior contract, ktory fixture testy overuju.
- `.planning/codebase/TESTING.md` — aktualny stav bez test runnera a odporucane smerovanie pre parser testy.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ZSEHDOLiveParser` v `custom_components/zse_hdo/parser.py` poskytuje centralny vstupny bod pre fixture-driven testovanie parser behavior.
- V parseri su oddelitelne funkcie vhodne na fixture validaciu (`_extract_javascript_array`, `_normalize_schedule`, `get_schedule`).

### Established Patterns
- Repo zatial nema test infra ani `tests/` strukturu; Phase 3 ju musi zaviesť minimalisticky.
- Parser ma standalone smoke `main()` flow, ale to nie je automatizovany test gate.

### Integration Points
- Fixture testy musia validovat parser vystupny shape, ktory konzumuje coordinator/sensor vrstva.
- Regression signal ma byt jasny cez test fail pred runtime overenim v HA.

</code_context>

<specifics>
## Specific Ideas

- Preferovat fixture scenare, ktore simulujú realne zmeny zdrojovej stranky (`zsdis.sk`) a parser edge handling.

</specifics>

<deferred>
## Deferred Ideas

- Rozsiahla corner-case matica parser vstupov nad minimum pre `PARS-04`.
- Home Assistant test harness (`pytest-homeassistant-custom-component`) pre neskorsiu fazu mimo scope Phase 3.

</deferred>

---

*Phase: 03-parser-verification-fixtures*
*Context gathered: 2026-04-29*
