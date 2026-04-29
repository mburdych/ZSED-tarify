# Requirements: ZSE HDO Live Home Assistant Integracia

**Defined:** 2026-04-29
**Last sync with shipped reality:** 2026-04-29 (v1.0.8)
**Core Value:** Stabilna a spolahliva integracia, ktora korektne cita harmonogram zo `www.zsdis.sk` a zrozumitelne ho prezentuje na Home Assistant dashboarde.

## v1 Requirements

Requirements for the v1 release. Status: **Validated** = implemented and shipped (v1.0.x), **Active** = still open in roadmap.

### Parser Correctness

- [x] **PARS-01** *(validated v1.0.8)*: Integracia stiahne zdrojove data zo `zsdis.sk` asynchronne bez blokovania Home Assistant event loop.
- [x] **PARS-02** *(validated v1.0.8)*: Parser premeni zdrojove data na stabilny interny model (`workday`/`weekend` low-tariff intervaly) so schema-konzistentnym vystupom.
- [x] **PARS-03** *(validated v1.0.8)*: Parser/coordinator korektne zlyha s diagnostickou chybou, ak sa format zdroja zmeni mimo podporovanej struktury (`UpdateFailed` + log).
- [ ] **PARS-04**: Parser je overeny fixture testami pre bezne aj hranicne varianty vstupu.

### Tariff Logic

- [x] **TIME-01** *(validated v1.0.8)*: Integracia korektne urci aktualny tarif pre aktualny cas a den.
- [x] **TIME-02** *(validated v1.0.8)*: Integracia korektne vypocita nasledujuci prechod tarify (`next_switch`).
- [x] **TIME-03** *(validated v1.0.8 commit `9a46238`)*: Logika osetri prechod cez polnoc a vikend/pracovny den.
- [x] **TZ-01**: Konzistentne pouzitie HA `dt_util` namiesto `datetime.now()` v parseri/sensoroch (timezone awareness).
- [x] **CODE-01**: Tariff/midnight kalkulus je v jednom mieste (dnes duplikovany v `parser._calculate_current_tariff`, `ZSEHDOTariffSensor.is_on`, `ZSEHDONextSwitchSensor._get_next_switch`).

### Reliability

- [x] **RELI-01** *(validated v1.0.8)*: `ZSEHDOCoordinator` (`DataUpdateCoordinator`) je jediny zdroj refresh logiky a cache pre vsetky entity.
- [x] **RELI-02** *(validated v1.0.8 commit `9a46238`)*: Pri docasnom vypadku zdroja integracia pouzije posledne uspesne data (`_last_known_data`).
- [ ] **RELI-03**: Explicitny retry/backoff pri opakovanych chybach (dnes spoliha na default HA refresh + dlhsie scheduled intervaly).
- [ ] **RELI-04**: Stav zastaranosti dat je explicitne dostupny pre uzivatela ako odlisny entity atribut/sensor (vek poslednej uspesnej aktualizacie, nielen timestamp).

### Home Assistant Presentation

- [x] **HAPR-01** *(validated v1.0.8)*: Integracia poskytne 3 entity: `binary_sensor` aktualnej tarify, `sensor` najblizsieho prechodu, `sensor` denneho rozpisu.
- [x] **HAPR-02** *(validated v1.0.8)*: Entity maju stabilne `unique_id` (`zse_hdo_<N>_*`), zrozumitelne atributy a metadate vhodne pre dashboard pouzitie.
- [x] **HAPR-03** *(validated v1.0.8 cez `EXAMPLES.md`)*: Dashboard prezentacia je prehladna pre bezne komunitne pouzitie (zakladna `entities` karta + Mushroom/card-mod recepty).

### Configuration & Operability

- [x] **CONF-01** *(validated v1.0.8)*: Integracia ma funkcny config flow s dynamicky nacitanym dropdownom HDO cisel zo `zsdis.sk`.
- [x] **CONF-02** *(validated v1.0.8)*: Options flow umoznuje zmenu `update_frequency` bez znovu pridania integracie.
- [ ] **CONF-03**: Diagnostika/logy umoznia odlisit fetch problem, parse problem a tariff-logic chybu (dnes splyvaju do generickej `error fetching HDO data`).

### Release Readiness *(novovznikla kategoria — viz Phase 7)*

- [ ] **RELEASE-01**: HACS validacia (`hacs.json` + `manifest.json` korektne; tag verzie zodpoveda manifest version-u).
- [ ] **RELEASE-02**: README changelog je synchronny s `manifest.json:version` pri kazdom release.
- [ ] **RELEASE-03**: Manualny smoke test v cistom HA dev instance (config flow → 3 entity → karta z `EXAMPLES.md`) pred publikaciou.
- [ ] **RELEASE-04**: Dokumentacny suhrn (CLAUDE.md, EXAMPLES.md, README HDO list) je synchronny so spravanim kodu.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Value Add

- **VADD-01**: Integracia ponukne pokrocile helper entity (napr. remaining low-tariff window).
- **VADD-02**: Integracia ponukne pripraveny blueprint balicek pre bezne automatizacie.
- **VADD-03**: Integracia podpori notifikacie pri zmenach harmonogramu na zdroji.

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
| PARS-01 | Phase 1 | Validated v1.0.8 |
| PARS-02 | Phase 1 | Validated v1.0.8 |
| PARS-03 | Phase 1 | Validated v1.0.8 |
| PARS-04 | Phase 3 | Active |
| TIME-01 | Phase 2 | Validated v1.0.8 |
| TIME-02 | Phase 2 | Validated v1.0.8 |
| TIME-03 | Phase 2 | Validated v1.0.8 |
| TZ-01 | Phase 2 | Active |
| CODE-01 | Phase 2 | Active |
| RELI-01 | Phase 4 | Validated v1.0.8 |
| RELI-02 | Phase 4 | Validated v1.0.8 |
| RELI-03 | Phase 4 | Active |
| RELI-04 | Phase 4 | Active |
| HAPR-01 | Phase 5 | Validated v1.0.8 |
| HAPR-02 | Phase 5 | Validated v1.0.8 |
| HAPR-03 | Phase 5 | Validated v1.0.8 |
| CONF-01 | Phase 6 | Validated v1.0.8 |
| CONF-02 | Phase 6 | Validated v1.0.8 |
| CONF-03 | Phase 6 | Active |
| RELEASE-01 | Phase 7 | Active |
| RELEASE-02 | Phase 7 | Active |
| RELEASE-03 | Phase 7 | Active |
| RELEASE-04 | Phase 7 | Active |

**Coverage:**
- v1 requirements: 23 total (17 original + 2 newly captured + 4 release-readiness)
- Validated in v1.0.8: 13
- Active: 10
- Mapped to phases: 23 / Unmapped: 0

---
*Requirements defined: 2026-04-29*
*Last updated: 2026-04-29 — synced with v1.0.8 reality, fixed `zsed.sk` → `zsdis.sk`, added TZ-01/CODE-01/RELEASE-* requirements.*
