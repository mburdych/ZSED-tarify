# ZSE HDO Live Home Assistant Integracia

*(repo: `ZSED-tarify`, integracny domain: `zse_hdo`, distribucia: HACS)*

## What This Is

Tento projekt je komunitne dostupna Home Assistant integracia, ktora sleduje HDO tarify Zapadoslovenskej distribucnej.
Integracia parsuje JS-pole zo stranky `www.zsdis.sk/Uvod/Online-sluzby/Casy-prepinania-nizkej-a-vysokej-tarify`, vytvara entity v Home Assistant a prezentuje ich v prehladnej podobe na dashboarde.
Ciel je dlhodobo stabilny plugin, ktory ostane pouzitelny aj pocas priebeznych zlepseni.

## Core Value

Stabilna a spolahliva integracia, ktora korektne cita harmonogram zo `zsdis.sk` a zrozumitelne ho prezentuje na Home Assistant dashboarde.

## Requirements

### Validated

Implementovane pred zalozenim tohto roadmap-u, overene v aktualne distribuovanej verzii **v1.0.8**:

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

- [ ] **PARS-04** — fixture testy pre parser (zatial nie je ziadny test runner v repo).
- [ ] **RELI-03** — explicitny retry/backoff pri opakovanych chybach (dnes spoliha na default HA refresh).
- [ ] **RELI-04** — uzivatelsky citatelna *staleness* (vek poslednej uspesnej aktualizacie ako entitny atribut/sensor).
- [ ] **CONF-03** — diagnostika musi v logoch jednoznacne odlisit fetch / parse / tariff-logic chyby.
- [ ] **CODE-01** *(noveho razenia)* — duplicita tariff/midnight kalkulu medzi `parser._calculate_current_tariff`, `ZSEHDOTariffSensor.is_on` a `ZSEHDONextSwitchSensor._get_next_switch` — single source of truth.
- [ ] **TZ-01** *(noveho razenia)* — konzistentne pouzitie `homeassistant.util.dt` namiesto `datetime.now()` v parseri/sensoroch (HA timezone awareness).

### Out of Scope

| Feature | Reason |
|---------|--------|
| Integracia dalsich zdrojov mimo `zsdis.sk` | Priorita je stabilita jedneho zdroja; iny operator ma iny format |
| Priame ovladanie spotrebicov v integracii | Patri do automations/blueprints, nie do data integracii |
| Vlastny charting engine v integracii | HA dashboard + komunitne HACS karty (Mushroom, card-mod) staci — vidime v `EXAMPLES.md` |
| Frontend JS karta (HACS plugin typ `plugin`) | Dashboard recept v YAML je dostatocny; vlastna karta = oddeleny repo + HACS submission |

## Context

Projekt je zamerany na komunitne pouzitie ako verejne zdielany plugin distribuovany cez HACS Custom Repository.
Zdrojova funkcionalita je v `custom_components/zse_hdo/` a je v aktivnej distribucii (v1.0.8).
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
| Prioritou parsera je presnost dat | Nekorektne hodnoty znizuju doveru a pouzitelnost integracie | Validated v1.0.8 |
| Prioritou prezentacie su dashboardy v Home Assistant | Koncovy uzivatel hodnotu vidi najma cez dashboard | Validated v1.0.8 (3 entity + EXAMPLES.md recepty) |
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
*Last updated: 2026-04-29 — synced with shipped v1.0.8 reality, fixed source URL (zsed.sk → zsdis.sk).*
