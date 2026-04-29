# ROADMAP: ZSE HDO Live Home Assistant Integracia

**Generated:** 2026-04-29
**Last sync with shipped reality:** 2026-04-29 (v1.0.8)
**Granularity:** fine
**Total v1 requirements:** 23
**Coverage:** 23/23 mapped (13 Validated v1.0.8, 10 Active)

## Phases

- [x] **Phase 1: Async Data Fetch & Parser Contract** *(validated v1.0.8)* — Integracia spolahlivo a asynchronne nacita zdroj a validuje parser vstupny kontrakt.
- [~] **Phase 2: Tariff Time Semantics** *(partial v1.0.8 — TZ-01/CODE-01 open)* — Integracia korektne rozhoduje aktualny tarif a dalsi prechod vo vsetkych casovych hranach.
- [x] **Phase 3: Parser Verification Fixtures** — Parser spravanie je overene automatizovanymi fixture testami pre bezne aj hranicne vstupy. (completed 2026-04-29)
- [~] **Phase 4: Coordinator Reliability & Staleness** *(partial v1.0.8 — RELI-03/RELI-04 open)* — Refresh, cache fallback, backoff a staleness su predvidatelne a citatelne pre uzivatela.
- [x] **Phase 5: Home Assistant Entity Presentation** *(validated v1.0.8)* — Entity a dashboard vystup su konzistentne, stabilne a prehladne pre komunitne pouzitie.
- [~] **Phase 6: Configurability & Diagnostics** *(partial v1.0.8 — CONF-03 open)* — Konfiguracia a diagnostika umoznia bezne operacne zmeny a rychlejsie riesenie problemov.
- [ ] **Phase 7: Release Readiness & v1 Checkpoint** — Finalna milestone-uroven kontrola pred publikaciou kazdej verzie cez HACS.

## Phase Details

### Phase 1: Async Data Fetch & Parser Contract
**Goal**: Integracia bez blokovania nacita data zo `zsdis.sk` a parser ich prevedie do stabilneho interneho modelu s jasnym zlyhanim pri nekompatibilnom formate.
**Depends on**: Nothing (first phase)
**Requirements**: PARS-01, PARS-02, PARS-03
**Status**: **Validated v1.0.8** — vsetky 3 requirements implementovane v `parser.py` + `coordinator.py`.
**Success Criteria** (what must be TRUE):
1. ✅ Pouzivatel vie integraciu spustit bez zasekov Home Assistant event loop pocas nacitavania dat.
2. ✅ Entitne data sa po refreshi naplnia konzistentne v rovnakom tvare pri opakovanych nahraniach rovnakeho vstupu.
3. ✅ Pri zmene zdrojoveho formatu je v logu diagnosticka chyba, ktora jednoznacne hovori o parse kontrakte.
**Plans**: TBD (retroaktivne — Phase 7 audit)

### Phase 2: Tariff Time Semantics
**Goal**: Uzivatel dostane korektny aktualny tarif a predikovany najblizsi prechod bez chyb na hraniciach casu, s konzistentnou TZ-aware logikou v jednom mieste.
**Depends on**: Phase 1
**Requirements**: TIME-01, TIME-02, TIME-03, **TZ-01**, **CODE-01**
**Status**: **Partial** — TIME-01/02/03 validated v1.0.8 (commit `9a46238`); TZ-01 a CODE-01 zostavaju otvorene.
**Success Criteria** (what must be TRUE):
1. ✅ V lubovolnom case dna sa v entite zobrazi spravny aktualny tarif podla harmonogramu.
2. ✅ Atribut/prehlad nasledujuceho prechodu zodpoveda realnemu najblizsiemu prepnutiu.
3. ✅ Spravanie ostava korektne pri prechode cez polnoc a medzi pracovnym dnom a vikendom.
4. ⏳ Vsetky datum/cas vypocty pouzivaju `homeassistant.util.dt` (HA timezone), nie `datetime.now()`.
5. ⏳ Tariff/midnight kalkulus existuje len v jednom mieste; sensory volaju spolocnu helper funkciu.
**Plans**: 2 plans
Plans:
- [x] 02-01-PLAN.md — Zavedenie shared time-semantics helper vrstvy a parser migracia na HA `dt_util`.
- [x] 02-02-PLAN.md — Sensor migracia na shared helper + boundary verifikacia v HA runtime.

### Phase 3: Parser Verification Fixtures
**Goal**: Parser korektnost je preukazatelna opakovatelne cez fixture testy pre standardne aj problemove vstupy.
**Depends on**: Phase 1, Phase 2
**Requirements**: PARS-04
**Status**: **Not started** — repo zatial nema test runner ani fixtures.
**Success Criteria** (what must be TRUE):
1. Pri beznych fixture vstupoch parser vracia ocakavany vystup bez manualnych zasahov.
2. Pri hranicnych fixture vstupoch parser bud vrati korektny model, alebo zlyha predvidatelnou diagnostickou chybou.
3. Regresia v parseri sa prejavi ako fail testu este pred nasadenim do Home Assistant.
**Plans**: 1 plan
Plans:
- [x] 03-01-PLAN.md — Zavedenie offline fixture parser test stacku (`pytest` + `pytest-asyncio`) s deterministickymi kontraktmi pre extract/normalize/get_schedule.

### Phase 4: Coordinator Reliability & Staleness
**Goal**: Refresh politika a fallback mechanizmy zabezpecia stabilny chod entit aj pocas docasnych problemov zdroja, s explicitne citatelnym vekom dat.
**Depends on**: Phase 1, Phase 2
**Requirements**: RELI-01, RELI-02, RELI-03, RELI-04
**Status**: **Partial** — RELI-01/02 validated v1.0.8 (commit `9a46238`); RELI-03/04 zostavaju otvorene.
**Success Criteria** (what must be TRUE):
1. ✅ Vsetky entity citaju data cez jednotnu coordinator refresh/cache vrstvu.
2. ✅ Pri docasnom vypadku zdroja ostavaju entity dostupne s poslednymi uspesnymi datami.
3. ⏳ Refresh ma explicitny retry/backoff a nevytvara nadmernu zataz na zdroj pri opakovanej chybe.
4. ⏳ Pouzivatel vie z entity zistit *vek* poslednej uspesnej aktualizacie (nielen timestamp).
**Plans**: 2 plans
Plans:
- [x] 04-01-PLAN.md — Zavedenie coordinator reliability state stroja s explicitnym retry/backoff a stale metadata pri fallbacku.
- [ ] 04-02-PLAN.md — Propagacia stale/recovery metadata do existujucich entity atributov a recovery regresne overenie.

### Phase 5: Home Assistant Entity Presentation
**Goal**: Uzivatel ma k dispozicii stabilne entity a prehladny dashboardovy vystup pre kazdodenne pouzitie.
**Depends on**: Phase 2, Phase 4
**Requirements**: HAPR-01, HAPR-02, HAPR-03
**Status**: **Validated v1.0.8** — 3 entity + Mushroom/card-mod recepty v `EXAMPLES.md`.
**Success Criteria** (what must be TRUE):
1. ✅ Uzivatel vidi konzistentne entity pre aktualny tarif, dalsi prechod a denny rozpis.
2. ✅ Entity maju stabilne identifikatory a zrozumitelne atributy vhodne pre dashboard/automatizacie.
3. ✅ Bezne komunitne dashboard pouzitie funguje bez hlbokej customizacie (entities karta) aj s pokrocilym timeline barom (Mushroom + card-mod recept).
**Plans**: TBD (retroaktivne)
**UI hint**: yes

### Phase 6: Configurability & Diagnostics
**Goal**: Uzivatel vie integraciu jednoducho nastavit, upravit refresh spravanie a rychlo rozpoznat typ problemy.
**Depends on**: Phase 4, Phase 5
**Requirements**: CONF-01, CONF-02, CONF-03
**Status**: **Partial** — CONF-01/02 validated v1.0.8; CONF-03 zostava otvorene.
**Success Criteria** (what must be TRUE):
1. ✅ Uzivatel vie integraciu nakonfigurovat cez funkcny Home Assistant config flow.
2. ✅ Uzivatel vie menit refresh spravanie bez odstranenia integracie cez options flow.
3. ⏳ Z diagnostiky/logov je jednoznacne odlisitelne, ci zlyhal fetch, parse alebo tariff logika (oddelene log markery / chybove triedy).
**Plans**: TBD

### Phase 7: Release Readiness & v1 Checkpoint
**Goal**: Pred kazdym `manifest.json:version` bumpom je integracia preverena ako celok — HACS validacia, README/CLAUDE/EXAMPLES sync, manualny smoke test v cistom HA, ziadny otvoreny v1 requirement bez explicitneho deferral.
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6
**Requirements**: RELEASE-01, RELEASE-02, RELEASE-03, RELEASE-04
**Status**: **Not started** — z hladiska checkpoint procesu; v1.0.8 bola uvedena ad-hoc.
**Success Criteria** (what must be TRUE):
1. `hacs.json` + `manifest.json` su konzistentne; git tag verzie zodpoveda `manifest.json:version`.
2. README changelog ma novu verziu s datumom + zoznamom zmien (release notes na uvod sekcie su projektovy zdroj).
3. Cisty Home Assistant dev instance dokaze: pridat integraciu cez UI → vidiet vsetky 3 entity → vykreslit zakladnu kartu + advanced timeline kartu z `EXAMPLES.md`.
4. CLAUDE.md, EXAMPLES.md a README zoznam HDO cisel su synchronne so spravanim kodu (ziadny "duch" v dokumentacii).
5. Vsetky Active requirements pre danu verziu su bud Validated, alebo explicitne posunute do v2 / Out of Scope so zaznamom v PROJECT.md.
**Plans**: TBD
**Cadence**: Phase 7 sa spusta pri kazdej predzevreznej milestone (kazdy v1.x release pred publikaciou).

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Async Data Fetch & Parser Contract | — | Validated v1.0.8 | 2026-01-13 |
| 2. Tariff Time Semantics | — | Partial v1.0.8 (TZ-01, CODE-01 open) | — |
| 3. Parser Verification Fixtures | 1/1 | Complete   | 2026-04-29 |
| 4. Coordinator Reliability & Staleness | — | Partial v1.0.8 (RELI-03, RELI-04 open) | — |
| 5. Home Assistant Entity Presentation | — | Validated v1.0.8 | 2026-01-13 |
| 6. Configurability & Diagnostics | — | Partial v1.0.8 (CONF-03 open) | — |
| 7. Release Readiness & v1 Checkpoint | 0/0 | Not started | — |

---
*Last updated: 2026-04-29 — synced with shipped v1.0.8 reality, fixed `zsed.sk` → `zsdis.sk`, added Phase 7 final checkpoint, statuses reflect existing implementation.*
