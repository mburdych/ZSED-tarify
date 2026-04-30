# Requirements: ZSE HDO Live Home Assistant Integracia

**Defined:** 2026-04-29
**Last sync with shipped reality:** 2026-04-30 (v1.2.1)
**Core Value:** Stabilna a spolahliva integracia, ktora korektne cita harmonogram zo `www.zsdis.sk` a zrozumitelne ho prezentuje na Home Assistant dashboarde.

## v1 Requirements

Requirements status: **Validated** = implemented and shipped (v1.2.0), **Implemented** = completed for next patch release.

### Parser Correctness

- [x] **PARS-01** *(validated v1.1.0)*: Integracia stiahne zdrojove data zo `zsdis.sk` asynchronne bez blokovania Home Assistant event loop.
- [x] **PARS-02** *(validated v1.1.0)*: Parser premeni zdrojove data na stabilny interny model (`workday`/`weekend` low-tariff intervaly) so schema-konzistentnym vystupom.
- [x] **PARS-03** *(validated v1.1.0)*: Parser/coordinator korektne zlyha s diagnostickou chybou, ak sa format zdroja zmeni mimo podporovanej struktury (`UpdateFailed` + log).
- [x] **PARS-04** *(validated v1.1.0)*: Parser je overeny fixture testami pre bezne aj hranicne varianty vstupu.

### Tariff Logic

- [x] **TIME-01** *(validated v1.1.0)*: Integracia korektne urci aktualny tarif pre aktualny cas a den.
- [x] **TIME-02** *(validated v1.1.0)*: Integracia korektne vypocita nasledujuci prechod tarify (`next_switch`).
- [x] **TIME-03** *(validated v1.1.0)*: Logika osetri prechod cez polnoc a vikend/pracovny den.
- [x] **TZ-01** *(validated v1.1.0)*: Konzistentne pouzitie HA `dt_util` namiesto `datetime.now()` v parseri/sensoroch (timezone awareness).
- [x] **CODE-01** *(validated v1.1.0)*: Tariff/midnight kalkulus je v jednom mieste.

### Reliability

- [x] **RELI-01** *(validated v1.1.0)*: `ZSEHDOCoordinator` (`DataUpdateCoordinator`) je jediny zdroj refresh logiky a cache pre vsetky entity.
- [x] **RELI-02** *(validated v1.1.0)*: Pri docasnom vypadku zdroja integracia pouzije posledne uspesne data (`_last_known_data`).
- [x] **RELI-03** *(validated v1.1.0)*: Explicitny retry/backoff pri opakovanych chybach.
- [x] **RELI-04** *(validated v1.1.0)*: Stav zastaranosti dat je explicitne dostupny pre uzivatela ako odlisny entity atribut/sensor (vek poslednej uspesnej aktualizacie, nielen timestamp).

### Home Assistant Presentation

- [x] **HAPR-01** *(validated v1.1.0)*: Integracia poskytne 3 entity: `binary_sensor` aktualnej tarify, `sensor` najblizsieho prechodu, `sensor` denneho rozpisu.
- [x] **HAPR-02** *(validated v1.1.0)*: Entity maju stabilne `unique_id` (`zse_hdo_<N>_*`), zrozumitelne atributy a metadate vhodne pre dashboard pouzitie.
- [x] **HAPR-03** *(validated v1.1.0 cez `EXAMPLES.md`)*: Dashboard prezentacia je prehladna pre bezne komunitne pouzitie (zakladna `entities` karta + Mushroom/card-mod recepty).

### Configuration & Operability

- [x] **CONF-01** *(validated v1.1.0)*: Integracia ma funkcny config flow s dynamicky nacitanym dropdownom HDO cisel zo `zsdis.sk`.
- [x] **CONF-02** *(validated v1.1.0)*: Options flow umoznuje zmenu `update_frequency` bez znovu pridania integracie.
- [x] **CONF-03** *(implemented v1.2.0)*: Diagnostika/logy umoznia odlisit fetch problem, parse problem a tariff-logic chybu (oddelene markery + testovatelny log contract).

### Release Readiness

- [x] **RELEASE-01** *(validated for v1.1.0)*: HACS validacia (`hacs.json` + `manifest.json` korektne; tag verzie zodpoveda manifest version-u).
- [x] **RELEASE-02** *(validated for v1.1.0)*: README changelog je synchronny s `manifest.json:version` pri kazdom release.
- [x] **RELEASE-03** *(validated for v1.1.0)*: Manualny smoke test v cistom HA dev instance (config flow → 3 entity → karta z `EXAMPLES.md`) pred publikaciou.
- [x] **RELEASE-04** *(validated for v1.1.0)*: Dokumentacny suhrn (CLAUDE.md, EXAMPLES.md, README HDO list) je synchronny so spravanim kodu.
- [x] **RELEASE-LOOP-01** *(implemented v1.2.0)*: Release checkpoint je kodifikovany ako opakovatelny workflow/checklist pouzitelny pri kazdom dalsom release.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Value Add

- **VADD-01** *(implemented v1.2.0)*: Integracia ponukne helper entitu pre remaining low-tariff window.
- **VADD-02** *(validated v1.2.1)*: Integracia ponukne pripraveny blueprint balicek pre bezne automatizacie.
- **VADD-03** *(implemented v1.2.0)*: Integracia podpori notifikacie pri zmenach harmonogramu na zdroji.

### Patch Stabilization *(nova kategoria pre v1.2.1)*

- [x] **STAB-01** *(validated v1.2.1)*: Patch stabilizacia po v1.2.0 odstrani zname edge-case regresie bez rozbitia entity/API kontraktu.

### Diagnostics Polish *(nova kategoria pre v1.2.1)*

- [x] **DIAG-02** *(validated v1.2.1)*: Diagnostika doplni operator-friendly guidance text a severity marker pre rychlejsie riesenie incidentov.

### Docs Hygiene *(nova kategoria pre v1.2.1)*

- [x] **DOCS-01** *(validated v1.2.1)*: README/EXAMPLES/planning dokumenty su po patch releasi konzistentne a bez zastaranych referencii.

## Out of Scope

Explicitly excluded for this wave to keep focus on stability and correctness.

| Feature | Reason |
|---------|--------|
| Integracia dalsich zdrojov mimo `zsdis.sk` | Priorita je stabilita jedneho zdroja; iny operator ma iny format |
| Priame ovladanie spotrebicov v integracii | Patri do automations/blueprints, nie do data integracii |
| Vlastny charting engine v integracii | HA dashboard + komunitne HACS karty (Mushroom, card-mod) staci |
| Frontend JS karta (HACS `plugin` typ) | Dashboard recept v YAML je dostatocny; vlastna karta = oddeleny repo + HACS submission |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PARS-01 | Phase 1 | Validated v1.1.0 |
| PARS-02 | Phase 1 | Validated v1.1.0 |
| PARS-03 | Phase 1 | Validated v1.1.0 |
| PARS-04 | Phase 3 | Validated v1.1.0 |
| TIME-01 | Phase 2 | Validated v1.1.0 |
| TIME-02 | Phase 2 | Validated v1.1.0 |
| TIME-03 | Phase 2 | Validated v1.1.0 |
| TZ-01 | Phase 2 | Validated v1.1.0 |
| CODE-01 | Phase 2 | Validated v1.1.0 |
| RELI-01 | Phase 4 | Validated v1.1.0 |
| RELI-02 | Phase 4 | Validated v1.1.0 |
| RELI-03 | Phase 4 | Validated v1.1.0 |
| RELI-04 | Phase 4 | Validated v1.1.0 |
| HAPR-01 | Phase 5 | Validated v1.1.0 |
| HAPR-02 | Phase 5 | Validated v1.1.0 |
| HAPR-03 | Phase 5 | Validated v1.1.0 |
| CONF-01 | Phase 6 | Validated v1.1.0 |
| CONF-02 | Phase 6 | Validated v1.1.0 |
| CONF-03 | Phase 8 | Implemented (v1.2.0) |
| RELEASE-01 | Phase 7 | Validated for v1.1.0 |
| RELEASE-02 | Phase 7 | Validated for v1.1.0 |
| RELEASE-03 | Phase 7 | Validated for v1.1.0 |
| RELEASE-04 | Phase 7 | Validated for v1.1.0 |
| RELEASE-LOOP-01 | Phase 11 | Implemented (v1.2.0) |
| VADD-01 | Phase 9 | Implemented (v1.2.0) |
| VADD-02 | Phase 13 | Validated (v1.2.1) |
| VADD-03 | Phase 10 | Implemented (v1.2.0) |
| STAB-01 | Phase 12 | Validated (v1.2.1) |
| DIAG-02 | Phase 14 | Validated (v1.2.1) |
| DOCS-01 | Phase 15 | Validated (v1.2.1) |

**Coverage:**
- v1 requirements: 23 total (17 original + 2 newly captured + 4 release-readiness)
- Validated in v1.1.0: 22
- Active: 0
- Mapped to phases: 23 / Unmapped: 0

---
*Requirements defined: 2026-04-29*
*Last updated: 2026-04-30 — v1.2.1 released and requirements STAB-01, VADD-02, DIAG-02, DOCS-01 validated.*
