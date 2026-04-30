---
phase: 02-tariff-time-semantics
verified: 2026-04-29T13:30:00Z
status: human_needed
score: 6/6 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Overit prechod tarify v HA na hranici intervalu"
    expected: "Binary sensor prepne presne na boundary case podla harmonogramu"
    why_human: "Vyžaduje zivy HA runtime clock/timezone kontext a realny entity refresh"
  - test: "Overit next_switch cez polnoc a zmenu day-type"
    expected: "Atributy time/to_tariff_name/day_type ostanu konzistentne s najblizsim realnym prechodom"
    why_human: "Vyžaduje runtime pozorovanie pred/po polnoci a weekend/workday hranici"
---

# Phase 2: Tariff Time Semantics Verification Report

**Phase Goal:** Uzivatel dostane korektny aktualny tarif a predikovany najblizsi prechod bez chyb na hraniciach casu, s konzistentnou TZ-aware logikou v jednom mieste.
**Verified:** 2026-04-29T13:30:00Z
**Status:** human_needed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | V lubovolnom case dna sa v entite zobrazi spravny aktualny tarif podla harmonogramu. | ✓ VERIFIED | `sensor.py` tarifny stav ide cez `is_low_tariff(..., now=dt_util.now())`; helper `calculate_current_tariff()` pouziva jednotny midnight predicate v `time_semantics.py`. |
| 2 | Atribut/prehlad nasledujuceho prechodu zodpoveda realnemu najblizsiemu prepnutiu. | ✓ VERIFIED | `sensor.py` deleguje na `calculate_next_switch()`; helper ma 3-krokovy flow (inside period -> next today -> tomorrow first period). |
| 3 | Spravanie ostava korektne pri prechode cez polnoc a medzi pracovnym dnom a vikendom. | ✓ VERIFIED | `is_time_in_period()` pouziva canonical `end < start => >= start OR < end`; `get_periods_for_datetime()` vybera workday/weekend podla candidate datetime. |
| 4 | Vsetky datum/cas vypocty pouzivaju `homeassistant.util.dt` (HA timezone), nie `datetime.now()`. | ✓ VERIFIED | `parser.py` a `sensor.py` pouzivaju `dt_util.now()`; runtime `datetime.now()` sa v tychto moduloch nenachadza. |
| 5 | Tariff/midnight kalkulus existuje len v jednom mieste; sensory volaju spolocnu helper funkciu. | ✓ VERIFIED | `sensor.py` importuje a vola `is_low_tariff`, `calculate_next_switch`, `get_periods_for_datetime` z `time_semantics.py`; parser tiez vola helper vrstvu. |
| 6 | Refaktor nemenil existujuci payload kontrakt parsera a entity atributov. | ✓ VERIFIED | `parser.get_schedule()` stale vracia `current_tariff`, `workday`, `weekend`, `last_updated`; v `sensor.py` ostali atributy `tariff_name`, `time`, `to_tariff_name`, `day_type`, `period_count`. |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `custom_components/zse_hdo/time_semantics.py` | Shared pure helper for day-type/in-period/current tariff/next switch | ✓ VERIFIED | Existuje, je substantive (parse/day-type/midnight/tariff/next-switch funkcie), importovana parserom aj senzormi. |
| `custom_components/zse_hdo/parser.py` | Parser deleguje na helper a HA-aware clock | ✓ VERIFIED | Import helperov + `dt_util.now()` pre current tariff, is_low, last_updated; py_compile pass. |
| `custom_components/zse_hdo/sensor.py` | Sensory deleguju logiku na helper vrstvu | ✓ VERIFIED | Ziadna lokalna tariff/midnight kalkulacia; wrappery volaju helper API; py_compile pass. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `parser.py` | `time_semantics.py` | import + helper calls | ✓ WIRED | `from .time_semantics import calculate_current_tariff, is_low_tariff` + volania v `_calculate_current_tariff` a `is_low_tariff_now`. |
| `parser.py` | `homeassistant.util.dt` | `dt_util.now()` | ✓ WIRED | `dt_util.now()` pouzite pre tariff vypocet aj `last_updated`. |
| `sensor.py` | `time_semantics.py` | shared helper calls | ✓ WIRED | `from .time_semantics import calculate_next_switch, get_periods_for_datetime, is_low_tariff` + volania v `is_on`, `_get_next_switch`, schedule attributoch. |
| `sensor.py` | `homeassistant.util.dt` | `dt_util.now()` | ✓ WIRED | Vsetky runtime vypocty idu cez `dt_util.now()`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `sensor.py` tariff sensor | `self.coordinator.data` -> `is_on` | `coordinator` payload z `parser.get_schedule()` | Yes (`workday`/`weekend` period data je parsovana zo ZSE JS arrays) | ✓ FLOWING |
| `sensor.py` next-switch sensor | `next_switch` payload | `calculate_next_switch(self.coordinator.data, now)` | Yes (helper vracia odvodeny datetime/time/to_tariff z real schedule) | ✓ FLOWING |
| `parser.py` current_tariff | `schedule` z `_normalize_schedule` | `household_rates` + `business_rates` z live HTML | Yes (tariff je vypocitany zo skutocnych intervalov) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Moduly fazy su syntakticky validne | `python -m py_compile custom_components/zse_hdo/parser.py custom_components/zse_hdo/sensor.py custom_components/zse_hdo/time_semantics.py` | Exit code 0 | ✓ PASS |
| Shared helper exportuje pozadovane API | `python -c "import importlib.util...; print(all(hasattr(...)))"` | `True` | ✓ PASS |
| Parser/sensor runtime clock je HA dt_util | static scan `parser.py` + `sensor.py` | `dt_util.now()` callsites pritomne, bez runtime `datetime.now()` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| TIME-01 | 02-01 | Korektny aktualny tarif pre aktualny cas/den | ✓ SATISFIED | Unified tariff vypocet v helperi, parser + sensor volaju rovnaky decision path. |
| TIME-02 | 02-02 | Korektny vypocet next_switch | ✓ SATISFIED | `calculate_next_switch()` implementuje nearest transition flow a sensor ho pouziva priamo. |
| TIME-03 | 02-02 | Korektne hranice polnoc + vikend/pracovny den | ✓ SATISFIED | Canonical midnight predicate + day-type selection by candidate datetime. |
| TZ-01 | 02-01, 02-02 | Konzistentne pouzitie HA `dt_util` | ✓ SATISFIED | Parser/sensor runtime logika bezi na `dt_util.now()`. |
| CODE-01 | 02-01, 02-02 | Tariff/midnight kalkulus v jednom mieste | ✓ SATISFIED | `time_semantics.py` je jediny kalkulacny zdroj; parser/sensor deleguju. |

Orphaned requirements for Phase 2 in `REQUIREMENTS.md`: none (all mapped IDs su pokryte plan frontmatter).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `custom_components/zse_hdo/time_semantics.py` | fallback block | `datetime.now()` fallback pri ImportError | ℹ️ Info | Neovplyvnuje HA runtime; je to standalone smoke fallback. |

### Human Verification Required

### 1. Midnight Boundary Transition in HA

**Test:** V HA dev instancii sledovat `binary_sensor` pre vybrane HDO tesne pred a po hranici low-tariff intervalu, vratane midnight-crossing intervalu.  
**Expected:** Stav sa prepne presne na hranici podla harmonogramu.  
**Why human:** Potrebny realny HA runtime clock/timezone kontext a entity refresh pipeline.

### 2. Next Switch Across Day-Type Change

**Test:** Overit `sensor` najblizsieho prepnutia pred/po polnoci a cez pracovny den/vikend, vratane atributov `time`, `to_tariff_name`, `day_type`.  
**Expected:** Predikcia je najblizsi realny prechod a atributy zostanu semanticky nezmenene.  
**Why human:** Vyžaduje runtime pozorovanie v zivej integracii.

### Gaps Summary

Automatizovane a staticke overenia neodhalili implementacne medzery oproti must-haves. Phase goal je kodovo dosiahnuty, ale finalny gate zostava `human_needed` pre runtime boundary potvrdenie v HA (manual checkpoint).

---

_Verified: 2026-04-29T13:30:00Z_  
_Verifier: Claude (gsd-verifier)_
