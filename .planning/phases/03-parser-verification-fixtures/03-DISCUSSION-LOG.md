# Phase 3: Parser Verification Fixtures - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 03-parser-verification-fixtures
**Areas discussed:** Test runner a rozsah testov

---

## Test runner a rozsah testov

### Q1: Aký baseline chceme uzamknúť pre túto fázu?

| Option | Description | Selected |
|--------|-------------|----------|
| pytest_minimal | Minimal pytest stack: pytest + pytest-asyncio, testujeme len parser layer | ✓ |
| ha_harness_now | Rovno aj HA test harness uz vo Phase 3 | |
| mixed_stepwise | Parser testy teraz, HA harness odlozit do dalsiej fazy | |

**User's choice:** pytest_minimal  
**Notes:** Scope sa drzi parser layer bez HA harnessu.

---

### Q2: Ako riesit siet v parser testoch?

| Option | Description | Selected |
|--------|-------------|----------|
| fixtures_no_network | Bez siete: parser testy idu vyhradne z lokalnych HTML fixtures | ✓ |
| mock_aiohttp | Mockovat aiohttp response objekty v unit testoch | |
| hybrid | Kombinacia fixtures + mockov podla testu | |

**User's choice:** fixtures_no_network  
**Notes:** Dovod je deterministicke a opakovatelne testovanie.

---

### Q3: Co je minimum pre splnenie PARS-04?

| Option | Description | Selected |
|--------|-------------|----------|
| core_cases | Klucove fixture pripady + fail pri regresii parser output shape | ✓ |
| broad_matrix | Siroka matica vsetkych corner-case variantov hned teraz | |
| smoke_only | Len zakladny smoke fixture test, ostatne neskor | |

**User's choice:** core_cases  
**Notes:** Priorita je prakticke minimum, nie maximalna matica.

---

## Claude's Discretion

- Naming a organizacia test/fixture suborov.
- Konkretna test helper API a rozdelenie pripadov do test modulov.

## Deferred Ideas

- Rozsiahla corner-case matica parser fixtures nad minimum pre PARS-04.
- Zavedenie HA test harnessu v samostatnom neskorsom scope.
