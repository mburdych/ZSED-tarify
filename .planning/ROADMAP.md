# ROADMAP: ZSE HDO Live Home Assistant Integracia

**Generated:** 2026-04-30
**Last sync with shipped reality:** 2026-04-30 (v1.2.1)
**Granularity:** fine
**Total tracked requirements:** 27
**Coverage:** 31/31 mapped (27 validated, 4 implemented for v1.2.1 patch)

## Phases

- [x] **Phase 1: Async Data Fetch & Parser Contract** *(validated v1.1.0)* — Integracia spolahlivo a asynchronne nacita zdroj a validuje parser vstupny kontrakt.
- [x] **Phase 2: Tariff Time Semantics** *(validated v1.1.0)* — Integracia korektne rozhoduje aktualny tarif a dalsi prechod vo vsetkych casovych hranach.
- [x] **Phase 3: Parser Verification Fixtures** *(validated v1.1.0)* — Parser spravanie je overene automatizovanymi fixture testami pre bezne aj hranicne vstupy.
- [x] **Phase 4: Coordinator Reliability & Staleness** *(validated v1.1.0)* — Refresh, cache fallback, backoff a staleness su predvidatelne a citatelne pre uzivatela.
- [x] **Phase 5: Home Assistant Entity Presentation** *(validated v1.1.0)* — Entity a dashboard vystup su konzistentne, stabilne a prehladne pre komunitne pouzitie.
- [~] **Phase 6: Configurability & Diagnostics** *(partial v1.1.0 — CONF-03 open)* — Konfiguracia a diagnostika umoznia bezne operacne zmeny a rychlejsie riesenie problemov.
- [x] **Phase 7: Release Readiness & v1 Checkpoint** *(executed for v1.1.0)* — Milestone-uroven kontrola bola aplikovana pred publikaciou v1.1.0.
- [x] **Phase 8: Diagnostic Signal Separation** *(implemented v1.2.0)* — CONF-03 dorucene: explicitne odlisovanie fetch/parse/tariff-logiky + payload markery.
- [x] **Phase 9: Remaining Low Tariff Helper Entity** *(implemented v1.2.0)* — VADD-01 dorucene: helper entita pre zostavajuci low-tariff window.
- [x] **Phase 10: Schedule Change Notification Hooks** *(implemented v1.2.0)* — VADD-03 dorucene: signalizacia zmen harmonogramu + docs automation hook.
- [x] **Phase 11: Release Loop Codification** *(implemented v1.2.0)* — RELEASE-LOOP-01 dorucene: opakovatelny release checklist workflow.
- [x] **Phase 12: Patch Stabilization Sweep** *(validated v1.2.1)* — STAB-01: stabilizacny patch pass nad v1.2.0 edge-case regresiami.
- [x] **Phase 13: Automation Blueprint Pack** *(validated v1.2.1)* — VADD-02: dorucenie blueprint balicka pre bezne HDO automacie.
- [x] **Phase 14: Diagnostics UX Polish** *(validated v1.2.1)* — DIAG-02: operator-friendly diagnostika (severity + guidance text).
- [x] **Phase 15: Docs Hygiene & Patch Release Prep** *(validated v1.2.1)* — DOCS-01: docs cleanup, consistency pass, patch-release priprava.

## Phase Details

### Phase 1: Async Data Fetch & Parser Contract
**Goal**: Integracia bez blokovania nacita data zo `zsdis.sk` a parser ich prevedie do stabilneho interneho modelu s jasnym zlyhanim pri nekompatibilnom formate.
**Depends on**: Nothing (first phase)
**Requirements**: PARS-01, PARS-02, PARS-03
**Status**: **Validated v1.1.0** — vsetky 3 requirements implementovane v `parser.py` + `coordinator.py`.
**Success Criteria** (what must be TRUE):
1. ✅ Pouzivatel vie integraciu spustit bez zasekov Home Assistant event loop pocas nacitavania dat.
2. ✅ Entitne data sa po refreshi naplnia konzistentne v rovnakom tvare pri opakovanych nahraniach rovnakeho vstupu.
3. ✅ Pri zmene zdrojoveho formatu je v logu diagnosticka chyba, ktora jednoznacne hovori o parse kontrakte.
**Plans**: TBD (retroaktivne — Phase 7 audit)

### Phase 2: Tariff Time Semantics
**Goal**: Uzivatel dostane korektny aktualny tarif a predikovany najblizsi prechod bez chyb na hraniciach casu, s konzistentnou TZ-aware logikou v jednom mieste.
**Depends on**: Phase 1
**Requirements**: TIME-01, TIME-02, TIME-03, **TZ-01**, **CODE-01**
**Status**: **Validated v1.1.0** — TIME-01/02/03 + TZ-01 + CODE-01 dorucene.
**Success Criteria** (what must be TRUE):
1. ✅ V lubovolnom case dna sa v entite zobrazi spravny aktualny tarif podla harmonogramu.
2. ✅ Atribut/prehlad nasledujuceho prechodu zodpoveda realnemu najblizsiemu prepnutiu.
3. ✅ Spravanie ostava korektne pri prechode cez polnoc a medzi pracovnym dnom a vikendom.
4. ✅ Vsetky datum/cas vypocty pouzivaju `homeassistant.util.dt` (HA timezone), nie `datetime.now()`.
5. ✅ Tariff/midnight kalkulus existuje v shared helper vrstve; sensory volaju spolocnu helper funkciu.
**Plans**: 2 plans
Plans:
- [x] 02-01-PLAN.md — Zavedenie shared time-semantics helper vrstvy a parser migracia na HA `dt_util`.
- [x] 02-02-PLAN.md — Sensor migracia na shared helper + boundary verifikacia v HA runtime.

### Phase 3: Parser Verification Fixtures
**Goal**: Parser korektnost je preukazatelna opakovatelne cez fixture testy pre standardne aj problemove vstupy.
**Depends on**: Phase 1, Phase 2
**Requirements**: PARS-04
**Status**: **Validated v1.1.0** — fixture testy su sucastou `tests/fixtures` + parser test suite.
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
**Status**: **Validated v1.1.0** — RELI-01/02/03/04 dorucene.
**Success Criteria** (what must be TRUE):
1. ✅ Vsetky entity citaju data cez jednotnu coordinator refresh/cache vrstvu.
2. ✅ Pri docasnom vypadku zdroja ostavaju entity dostupne s poslednymi uspesnymi datami.
3. ✅ Refresh ma explicitny retry/backoff a nevytvara nadmernu zataz na zdroj pri opakovanej chybe.
4. ✅ Pouzivatel vie z entity zistit *vek* poslednej uspesnej aktualizacie (nielen timestamp).
**Plans**: 2 plans
Plans:
- [x] 04-01-PLAN.md — Zavedenie coordinator reliability state stroja s explicitnym retry/backoff a stale metadata pri fallbacku.
- [x] 04-02-PLAN.md — Propagacia stale/recovery metadata do existujucich entity atributov a recovery regresne overenie.

### Phase 5: Home Assistant Entity Presentation
**Goal**: Uzivatel ma k dispozicii stabilne entity a prehladny dashboardovy vystup pre kazdodenne pouzitie.
**Depends on**: Phase 2, Phase 4
**Requirements**: HAPR-01, HAPR-02, HAPR-03
**Status**: **Validated v1.1.0** — 3 entity + Mushroom/card-mod recepty v `EXAMPLES.md`.
**Success Criteria** (what must be TRUE):
1. ✅ Uzivatel vidi konzistentne entity pre aktualny tarif, dalsi prechod a denny rozpis.
2. ✅ Entity maju stabilne identifikatory a zrozumitelne atributy vhodne pre dashboard/automatizacie.
3. ✅ Bezne komunitne dashboard pouzitie funguje bez hlbokej customizacie (entities karta) aj s pokrocilym timeline barom (Mushroom + card-mod recept).
**Plans**: 2 plans
Plans:
- [x] 05-01-PLAN.md — Zafixovanie entity presentation kontraktu cez automatizovane ID/attribute testy.
- [x] 05-02-PLAN.md — Docs/examples parity hardening s baseline dashboard kompatibilitou.
**UI hint**: yes

### Phase 6: Configurability & Diagnostics
**Goal**: Uzivatel vie integraciu jednoducho nastavit, upravit refresh spravanie a rychlo rozpoznat typ problemy.
**Depends on**: Phase 4, Phase 5
**Requirements**: CONF-01, CONF-02, CONF-03
**Status**: **Partial** — CONF-01/02 validated v1.1.0; CONF-03 zostava otvorene.
**Success Criteria** (what must be TRUE):
1. ✅ Uzivatel vie integraciu nakonfigurovat cez funkcny Home Assistant config flow.
2. ✅ Uzivatel vie menit refresh spravanie bez odstranenia integracie cez options flow.
3. ⏳ Z diagnostiky/logov je jednoznacne odlisitelne, ci zlyhal fetch, parse alebo tariff logika (oddelene log markery / chybove triedy).
**Plans**: TBD

### Phase 7: Release Readiness & v1 Checkpoint
**Goal**: Pred kazdym `manifest.json:version` bumpom je integracia preverena ako celok — HACS validacia, README/CLAUDE/EXAMPLES sync, manualny smoke test v cistom HA, ziadny otvoreny v1 requirement bez explicitneho deferral.
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6
**Requirements**: RELEASE-01, RELEASE-02, RELEASE-03, RELEASE-04
**Status**: **Validated for v1.1.0** — checkpoint bol vykonany pred release, ostava ako opakovatelna cadence.
**Success Criteria** (what must be TRUE):
1. `hacs.json` + `manifest.json` su konzistentne; git tag verzie zodpoveda `manifest.json:version`.
2. README changelog ma novu verziu s datumom + zoznamom zmien (release notes na uvod sekcie su projektovy zdroj).
3. Cisty Home Assistant dev instance dokaze: pridat integraciu cez UI → vidiet vsetky 3 entity → vykreslit zakladnu kartu + advanced timeline kartu z `EXAMPLES.md`.
4. CLAUDE.md, EXAMPLES.md a README zoznam HDO cisel su synchronne so spravanim kodu (ziadny "duch" v dokumentacii).
5. Vsetky Active requirements pre danu verziu su bud Validated, alebo explicitne posunute do v2 / Out of Scope so zaznamom v PROJECT.md.
**Plans**: TBD
**Cadence**: Phase 7 sa spusta pri kazdej predzevreznej milestone (kazdy v1.x release pred publikaciou).

### Phase 8: Diagnostic Signal Separation
**Goal**: Diagnostika je pre maintainera aj usera jednoznacna a testovatelna; kazdy failure path ma jasny marker.
**Depends on**: Phase 6
**Requirements**: CONF-03
**Status**: **Implemented v1.2.0**.
**Success Criteria** (what must be TRUE):
1. Log udalosti jednoznacne odlisuju fetch, parse a tariff-logic chyby.
2. Error metadata je konzistentna medzi parser/coordinator/sensor vrstvami.
3. Existuje regression test, ktory overi pritomnost markerov pri simulovanych chybach.
**Plans**:
- [x] 08-01-PLAN.md — Diagnostic marker separation + regression coverage.

### Phase 9: Remaining Low Tariff Helper Entity
**Goal**: Uzivatel vie bez sablon zistit, kolko casu ostava do konca aktualneho low-tariff okna.
**Depends on**: Phase 2, Phase 8
**Requirements**: VADD-01
**Status**: **Implemented v1.2.0**.
**Success Criteria** (what must be TRUE):
1. Nova helper entita vracia remaining low-tariff window v predvidatelnom tvare.
2. Entita je stabilna cez den, polnoc a prechody prac. den/vikend.
3. README/EXAMPLES obsahuje baseline pouzitie helper entity.
**Plans**:
- [x] 09-01-PLAN.md — Helper entity + boundary semantics tests + docs parity.

### Phase 10: Schedule Change Notification Hooks
**Goal**: Integracia poskytne signal pri zmene harmonogramu, na ktory sa da priamo naviazat notifikacia.
**Depends on**: Phase 3, Phase 8
**Requirements**: VADD-03
**Status**: **Implemented v1.2.0**.
**Success Criteria** (what must be TRUE):
1. Pri detekcii zmeny harmonogramu sa vytvori explicitny event/flag.
2. Zmena harmonogramu je rozlisena od bezneho periodickeho refreshu bez zmeny.
3. Dokumentacia obsahuje priklad automatizacie notifikacie.
**Plans**:
- [x] 10-01-PLAN.md — Schedule-change signal hooks + contract/docs updates.

### Phase 11: Release Loop Codification
**Goal**: Release checkpoint je formalizovany tak, aby bol opakovatelny a kratky pri kazdom dalsom releasi.
**Depends on**: Phase 8, Phase 9, Phase 10
**Requirements**: RELEASE-LOOP-01
**Status**: **Implemented v1.2.0**.
**Success Criteria** (what must be TRUE):
1. Existuje jednoznacny release checklist/workflow v planning/docs artefaktoch.
2. Checklist pokryva HACS/manifest/changelog/smoke test/docs sync.
3. Pri patch release je mozne checkpoint vykonat bez ad-hoc krokov.
**Plans**:
- [x] 11-01-PLAN.md — Release loop codification into repeatable checklist workflow.

### Phase 12: Patch Stabilization Sweep
**Goal**: Stabilizovat patch regresie po v1.2.0 bez zmeny externeho entity contractu.
**Depends on**: Phase 11
**Requirements**: STAB-01
**Status**: **Validated v1.2.1**.
**Success Criteria** (what must be TRUE):
1. Identifikovane edge-case bugy su opravene bez narusenia existujucich test kontraktov.
2. Full regression suite ostava zelena po patch fixoch.
3. Ziadna zmena stable entity IDs/attribute contract surface.
**Plans**:
- [x] 12-01-PLAN.md — Stabilization sweep for low-remaining boundary behavior.

### Phase 13: Automation Blueprint Pack
**Goal**: Dodat pripraveny blueprint balicek pre bezne user flows (bojler, reminder, tariff notifications).
**Depends on**: Phase 12
**Requirements**: VADD-02
**Status**: **Validated v1.2.1**.
**Success Criteria** (what must be TRUE):
1. Blueprint-y su importovatelne v HA bez manualnych fixov.
2. Pokryte su aspon 2-3 najbeznejsie HDO automation scenare.
3. Dokumentacia obsahuje jednoduche kroky pre pouzitie blueprintov.
**Plans**:
- [x] 13-01-PLAN.md — Blueprint pack for common HDO user flows.

### Phase 14: Diagnostics UX Polish
**Goal**: Zvysit citatelnost diagnostiky pre operatorov cez severity a guidance text.
**Depends on**: Phase 12
**Requirements**: DIAG-02
**Status**: **Validated v1.2.1**.
**Success Criteria** (what must be TRUE):
1. Diagnosticke payloady obsahuje severity marker pre jednoduche triage.
2. Guidance text navadza na dalsi krok pri beznych incidentoch.
3. Testy overuju pritomnost novych diagnostickych poli.
**Plans**:
- [x] 14-01-PLAN.md — Diagnostics severity/guidance payload polish.

### Phase 15: Docs Hygiene & Patch Release Prep
**Goal**: Pred patch releasom zabezpecit uplnu konzistenciu docs/planning artefaktov.
**Depends on**: Phase 13, Phase 14
**Requirements**: DOCS-01
**Status**: **Validated v1.2.1**.
**Success Criteria** (what must be TRUE):
1. README/EXAMPLES/planning subory su bez driftu a zastaranych referencii.
2. Changelog a release checklist odzrkadluju realny scope patch releasu.
3. Projekt je pripraveny na patch publish bez ad-hoc docs doplnkov.
**Plans**:
- [x] 15-01-PLAN.md — Milestone docs hygiene + release prep sync.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Async Data Fetch & Parser Contract | — | Validated v1.1.0 | 2026-04-29 |
| 2. Tariff Time Semantics | 2/2 | Validated v1.1.0 | 2026-04-29 |
| 3. Parser Verification Fixtures | 1/1 | Validated v1.1.0 | 2026-04-29 |
| 4. Coordinator Reliability & Staleness | 2/2 | Validated v1.1.0 | 2026-04-29 |
| 5. Home Assistant Entity Presentation | 2/2 | Validated v1.1.0 | 2026-04-29 |
| 6. Configurability & Diagnostics | — | Partial v1.1.0 (CONF-03 open) | — |
| 7. Release Readiness & v1 Checkpoint | — | Validated for v1.1.0 | 2026-04-29 |
| 8. Diagnostic Signal Separation | 1/1 | Implemented v1.2.0 | 2026-04-30 |
| 9. Remaining Low Tariff Helper Entity | 1/1 | Implemented v1.2.0 | 2026-04-30 |
| 10. Schedule Change Notification Hooks | 1/1 | Implemented v1.2.0 | 2026-04-30 |
| 11. Release Loop Codification | 1/1 | Implemented v1.2.0 | 2026-04-30 |
| 12. Patch Stabilization Sweep | 1/1 | Validated v1.2.1 | 2026-04-30 |
| 13. Automation Blueprint Pack | 1/1 | Validated v1.2.1 | 2026-04-30 |
| 14. Diagnostics UX Polish | 1/1 | Validated v1.2.1 | 2026-04-30 |
| 15. Docs Hygiene & Patch Release Prep | 1/1 | Validated v1.2.1 | 2026-04-30 |

---
*Last updated: 2026-04-30 — v1.2.1 released and phases 12-15 validated.*
