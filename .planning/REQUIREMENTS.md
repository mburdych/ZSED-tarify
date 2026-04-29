# Requirements: ZSED Tarify Home Assistant Integracia

**Defined:** 2026-04-29
**Core Value:** Stabilna a spolahliva integracia, ktora korektne cita data zo zsed.sk a zrozumitelne ich prezentuje na Home Assistant dashboarde.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Parser Correctness

- [ ] **PARS-01**: Integracia stiahne zdrojove data zo zsed.sk asynchronne bez blokovania Home Assistant event loop.
- [ ] **PARS-02**: Parser premeni zdrojove data na stabilny interny model so schema validaciou.
- [ ] **PARS-03**: Parser korektne zlyha s diagnostickou chybou, ak sa format zdroja zmeni mimo podporovanej struktury.
- [ ] **PARS-04**: Parser je overeny fixture testami pre bezne aj hranicne varianty vstupu.

### Tariff Logic

- [ ] **TIME-01**: Integracia korektne urci aktualny tarif pre aktualny cas a den.
- [ ] **TIME-02**: Integracia korektne vypocita nasledujuci prechod tarify.
- [ ] **TIME-03**: Logika korektne osetri prechod cez polnoc, vikend/pracovny den a casovu zonu.

### Reliability

- [ ] **RELI-01**: DataUpdateCoordinator je jediny zdroj refresh logiky a cache pre vsetky entity.
- [ ] **RELI-02**: Pri docasnom vypadku zdroja integracia pouzije posledne uspesne data (last known good).
- [ ] **RELI-03**: Integracia pouziva konzervativny retry/backoff pristup bez agresivneho prehltenia zdroja.
- [ ] **RELI-04**: Stav zastaranosti dat je explicitne dostupny pre uzivatela (napr. last update age).

### Home Assistant Presentation

- [ ] **HAPR-01**: Integracia poskytne konzistentne entity pre aktualny tarif, dalsi prechod a denny rozpis.
- [ ] **HAPR-02**: Entity maju stabilne IDs, zrozumitelne atributy a vhodne metadate pre dashboard pouzitie.
- [ ] **HAPR-03**: Dashboard prezentacia je prehladna pre bezne komunitne pouzitie bez nutnosti hlbokej customizacie.

### Configuration & Operability

- [ ] **CONF-01**: Integracia ma funkcny config flow pre nastavenie zdroja a vstupnych parametrov.
- [ ] **CONF-02**: Integracia umozni zmenu refresh spravania cez options flow.
- [ ] **CONF-03**: Diagnostika/logy umoznia odlisit fetch problem, parse problem a logicku chybu.

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
| Integracia dalsich zdrojov mimo zsed.sk | Priorita je stabilita jedneho zdroja |
| Priame ovladanie spotrebicov v integracii | Zodpovednost ma byt v automations/blueprints, nie v data integracii |
| Vlastny charting engine | Home Assistant dashboard uz poskytuje vhodne vizualizacie |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PARS-01 | Phase 1 | Pending |
| PARS-02 | Phase 1 | Pending |
| PARS-03 | Phase 1 | Pending |
| PARS-04 | Phase 3 | Pending |
| TIME-01 | Phase 2 | Pending |
| TIME-02 | Phase 2 | Pending |
| TIME-03 | Phase 2 | Pending |
| RELI-01 | Phase 4 | Pending |
| RELI-02 | Phase 4 | Pending |
| RELI-03 | Phase 4 | Pending |
| RELI-04 | Phase 4 | Pending |
| HAPR-01 | Phase 5 | Pending |
| HAPR-02 | Phase 5 | Pending |
| HAPR-03 | Phase 5 | Pending |
| CONF-01 | Phase 6 | Pending |
| CONF-02 | Phase 6 | Pending |
| CONF-03 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-04-29*
*Last updated: 2026-04-29 after roadmap mapping*
