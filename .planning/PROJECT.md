# ZSE HDO Live Home Assistant Integracia

*(repo: `ZSED-tarify`, integracny domain: `zse_hdo`, distribucia: HACS)*

## What This Is

Tento projekt je komunitne dostupna Home Assistant integracia, ktora sleduje HDO tarify Zapadoslovenskej distribucnej.
Integracia parsuje JS-pole zo stranky `www.zsdis.sk/Uvod/Online-sluzby/Casy-prepinania-nizkej-a-vysokej-tarify`, vytvara entity v Home Assistant a prezentuje ich v prehladnej podobe na dashboarde.
Ciel je dlhodobo stabilny plugin, ktory ostane pouzitelny aj pocas priebeznych zlepseni.

## Core Value

Stabilna a spolahliva integracia, ktora korektne cita harmonogram zo `zsdis.sk` a zrozumitelne ho prezentuje na Home Assistant dashboarde.

## Current Milestone: v1.2.1 Patch + Blueprint Expansion

**Goal:** Dorucit patch stabilizaciu po v1.2.0 a rozsirenie o blueprint balicek automatizacii.

**Target features:**
- Dorucit `VADD-02` (blueprint balicek pre bezne automacie)
- Stabilizacne patch fixy po release `v1.2.0` (edge-case + regression cleanup)
- Diagnosticky polish nad ramec `CONF-03` (operator readability)
- Docs cleanup a release-ready sync pre patch cadence

## Requirements

### Validated

Implementovane a overene v aktualne distribuovanej verzii **v1.2.0**:

- [x] **PARS-01** — async fetch zo `zsdis.sk` cez `aiohttp` bez blokovania HA event loop.
- [x] **PARS-02** — parser produkuje stabilny interny model (`workday`/`weekend` polia s low-tariff intervalmi).
- [x] **PARS-03** — pri zmene formatu zdroja parser loguje diagnosticku chybu a coordinator vrati `UpdateFailed`.
- [x] **TIME-01** — aktualny tarif sa pocita zo schedule + aktualneho casu (vratane prelomu polnoci).
- [x] **TIME-02** — `next_switch` sensor vracia najblizsi prepinaci cas.
- [x] **TIME-03** — riesenie polnoci a vikend/pracovny den je hotove (commit `9a46238`).
- [x] **RELI-01** — jediny `ZSEHDOCoordinator` napaja vsetky 3 entity.
- [x] **RELI-02** — pri docasnom vypadku zdroja sa pouzije `_last_known_data` cache (commit `9a46238`).
- [x] **HAPR-01** — 3 entity: `binary_sensor` tarify, `sensor` next_switch, `sensor` today_schedule.
- [x] **HAPR-02** — stabilne `unique_id` (`zse_hdo_<N>_*`), zrozumitelne atributy pre dashboard.
- [x] **HAPR-03** — recepty pre Mushroom + card-mod kartu su zdokumentovane v `EXAMPLES.md`.
- [x] **CONF-01** — config flow s dynamicky nacitanym dropdownom HDO cisel.
- [x] **CONF-02** — options flow umoznuje menit `update_frequency` bez znovu pridania.

### Active

Nedostatky, ktore zostavaju otvorene v roadmap-e:

- [x] **VADD-02** — pripraveny blueprint balicek pre bezne automatizacie je validovany v `v1.2.1`.
- [x] **STAB-01** — patch stabilizacia po v1.2.0 je validovana bez zmeny contract surface v `v1.2.1`.
- [x] **DIAG-02** — diagnosticke hlasky/metadate so severity + guidance su validovane v `v1.2.1`.
- [x] **DOCS-01** — docs cleanup a consistency pass po v1.2.0 je validovany v `v1.2.1`.

### Out of Scope

| Feature | Reason |
|---------|--------|
| Integracia dalsich zdrojov mimo `zsdis.sk` | Priorita je stabilita jedneho zdroja; iny operator ma iny format |
| Priame ovladanie spotrebicov v integracii | Patri do automations/blueprints, nie do data integracii |
| Vlastny charting engine v integracii | HA dashboard + komunitne HACS karty (Mushroom, card-mod) staci — vidime v `EXAMPLES.md` |
| Frontend JS karta (HACS plugin typ `plugin`) | Dashboard recept v YAML je dostatocny; vlastna karta = oddeleny repo + HACS submission |

## Context

Projekt je zamerany na komunitne pouzitie ako verejne zdielany plugin distribuovany cez HACS Custom Repository.
Zdrojova funkcionalita je v `custom_components/zse_hdo/` a je v aktivnej distribucii (v1.2.0).
Primarny zdroj dat je `www.zsdis.sk`, kde su HDO harmonogramy ulozene ako embedded JavaScript polia (`household_rates`, `business_rates`).
Prezentacna priorita je kvalita dashboardu v HA — samotne nacitanie dat nie je hodnota; hodnota je co uzivatel vidi.

## Constraints

- **Source Dependency**: Data zo `zsdis.sk` su embedded JS pole, **nie verejne API**. Akakolvek zmena rozlozenia stranky alebo nazvov premennych zlomi parser.
- **Scraping Fragility**: Parser rucne walkuje zatvorky a robi JS→JSON rewrite (`_extract_javascript_array`) — narocne na audit. Akakolvek zmena formatu vyzaduje pristup parser-first.
- **Community Quality**: Plugin je urceny pre komunitu — stabilita a predvidatelnost spravania su klucove.
- **Home Assistant UX**: Vystup musi byt dobre pouzitelny v dashboardoch — samotna dostupnost dat nestaci.
- **Dashboard Contract via External HACS**: Pokrocile vizualne recepty (timeline bar) zavisia od `mushroom` a `card-mod` HACS pluginov. Tieto su odporucenie, nie tvrda dependency — zakladne entity musia fungovat aj bez nich.
- **Incremental Delivery**: Nove funkcie sa mozu objavit pocas vylepsovania — treba ich riadit bez narusenia stability.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Prioritou parsera je presnost dat | Nekorektne hodnoty znizuju doveru a pouzitelnost integracie | Validated v1.2.0 |
| Prioritou prezentacie su dashboardy v Home Assistant | Koncovy uzivatel hodnotu vidi najma cez dashboard | Validated v1.2.0 (4 entity + EXAMPLES.md recepty) |
| Scraping namiesto API | ZSE/ZSDIS neposkytuje verejne API — embedded JS pole je jediny dostupny zdroj | Accepted; kompenzovane fixture-test plánom (PARS-04) |
| Dashboard cez externe HACS pluginy, nie vlastna JS karta | Niksi maintenance burden; pluginy uz su zauzivane v komunite | Accepted; pokryte ako "out of scope" pre v1 |
| Default refresh frequency = `1week` | Harmonogram zdroja sa meni zriedka; setri zataz na `zsdis.sk` | Validated v1.0.5+ |
| Scope zatial ostava otvoreny pre nove funkcie | Pocas vylepsovania sa mozu objavit relevantne poziadavky | Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase/version reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-30 — milestone v1.2.1 released.*
