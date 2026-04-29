# ROADMAP: ZSED Tarify Home Assistant Integracia

**Generated:** 2026-04-29  
**Granularity:** fine  
**Total v1 requirements:** 17  
**Coverage:** 17/17 mapped

## Phases

- [ ] **Phase 1: Async Data Fetch & Parser Contract** - Integracia spolahlivo a asynchronne nacita zdroj a validuje parser vstupny kontrakt.
- [ ] **Phase 2: Tariff Time Semantics** - Integracia korektne rozhoduje aktualny tarif a dalsi prechod vo vsetkych casovych hranach.
- [ ] **Phase 3: Parser Verification Fixtures** - Parser spravanie je overene automatizovanymi fixture testami pre bezne aj hranicne vstupy.
- [ ] **Phase 4: Coordinator Reliability & Staleness** - Refresh, cache fallback, backoff a staleness su predvidatelne a citatelne pre uzivatela.
- [ ] **Phase 5: Home Assistant Entity Presentation** - Entity a dashboard vystup su konzistentne, stabilne a prehladne pre komunitne pouzitie.
- [ ] **Phase 6: Configurability & Diagnostics** - Konfiguracia a diagnostika umoznia bezne operacne zmeny a rychlejsie riesenie problemov.

## Phase Details

### Phase 1: Async Data Fetch & Parser Contract
**Goal**: Integracia bez blokovania nacita data zo zdroja a parser ich prevedie do stabilneho interneho modelu s jasnym zlyhanim pri nekompatibilnom formate.  
**Depends on**: Nothing (first phase)  
**Requirements**: PARS-01, PARS-02, PARS-03  
**Success Criteria** (what must be TRUE):
1. Pouzivatel vie integraciu spustit bez zasekov Home Assistant event loop pocas nacitavania dat.
2. Entitne data sa po refreshi naplnia konzistentne v rovnakom tvare pri opakovanych nahraniach rovnakeho vstupu.
3. Pri zmene zdrojoveho formatu je v logu diagnosticka chyba, ktora jednoznacne hovori o parse kontrakte.
**Plans**: TBD

### Phase 2: Tariff Time Semantics
**Goal**: Uzivatel dostane korektny aktualny tarif a predikovany najblizsi prechod bez chyb na hraniciach casu.  
**Depends on**: Phase 1  
**Requirements**: TIME-01, TIME-02, TIME-03  
**Success Criteria** (what must be TRUE):
1. V lubovolnom case dna sa v entite zobrazi spravny aktualny tarif podla harmonogramu.
2. Atribut/prehlad nasledujuceho prechodu zodpoveda realnemu najblizsiemu prepnutiu.
3. Spravanie ostava korektne aj pri prechode cez polnoc, medzi pracovnym dnom a vikendom a v aktivnej casovej zone.
**Plans**: TBD

### Phase 3: Parser Verification Fixtures
**Goal**: Parser korektnost je preukazatelna opakovatelne cez fixture testy pre standardne aj problemove vstupy.  
**Depends on**: Phase 1, Phase 2  
**Requirements**: PARS-04  
**Success Criteria** (what must be TRUE):
1. Pri beznych fixture vstupoch parser vracia ocakavany vystup bez manualnych zasahov.
2. Pri hranicnych fixture vstupoch parser bud vrati korektny model, alebo zlyha predvidatelnou diagnostickou chybou.
3. Regresia v parseri sa prejavi ako fail testu este pred nasadenim do Home Assistant.
**Plans**: TBD

### Phase 4: Coordinator Reliability & Staleness
**Goal**: Refresh politika a fallback mechanizmy zabezpecia stabilny chod entit aj pocas docasnych problemov zdroja.  
**Depends on**: Phase 1, Phase 2  
**Requirements**: RELI-01, RELI-02, RELI-03, RELI-04  
**Success Criteria** (what must be TRUE):
1. Vsetky entity citaju data cez jednotnu coordinator refresh/cache vrstvu.
2. Pri docasnom vypadku zdroja ostavaju entity dostupne s poslednymi uspesnymi datami.
3. Refresh nepouziva agresivne dotazovanie a nevytvara nadmernu zataz na zdroj.
4. Pouzivatel vie z entit zistit, ze data su zastarane (napr. vek poslednej aktualizacie).
**Plans**: TBD

### Phase 5: Home Assistant Entity Presentation
**Goal**: Uzivatel ma k dispozicii stabilne entity a prehladny dashboardovy vystup pre kazdodenne pouzitie.  
**Depends on**: Phase 2, Phase 4  
**Requirements**: HAPR-01, HAPR-02, HAPR-03  
**Success Criteria** (what must be TRUE):
1. Uzivatel vidi konzistentne entity pre aktualny tarif, dalsi prechod a denny rozpis.
2. Entity maju stabilne identifikatory a zrozumitelne atributy vhodne pre dashboard/automatizacie.
3. Bezne komunitne dashboard pouzitie funguje bez hlbokej customizacie.
**Plans**: TBD
**UI hint**: yes

### Phase 6: Configurability & Diagnostics
**Goal**: Uzivatel vie integraciu jednoducho nastavit, upravit refresh spravanie a rychlo rozpoznat typ problemy.  
**Depends on**: Phase 4, Phase 5  
**Requirements**: CONF-01, CONF-02, CONF-03  
**Success Criteria** (what must be TRUE):
1. Uzivatel vie integraciu nakonfigurovat cez funkcny Home Assistant config flow.
2. Uzivatel vie menit refresh spravanie bez odstranenia integracie cez options flow.
3. Z diagnostiky/logov je jasne odlisitelne, ci zlyhal fetch, parse alebo tarifna logika.
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Async Data Fetch & Parser Contract | 0/0 | Not started | - |
| 2. Tariff Time Semantics | 0/0 | Not started | - |
| 3. Parser Verification Fixtures | 0/0 | Not started | - |
| 4. Coordinator Reliability & Staleness | 0/0 | Not started | - |
| 5. Home Assistant Entity Presentation | 0/0 | Not started | - |
| 6. Configurability & Diagnostics | 0/0 | Not started | - |

