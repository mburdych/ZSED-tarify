# ZSED Tarify Home Assistant Integracia

## What This Is

Tento projekt je komunitne dostupna Home Assistant integracia pre data zo `zsed.sk`.
Integracia parsuje webove data, vytvara entity v Home Assistant a prezentuje ich v prehladnej podobe na dashboarde.
Ciel je dlhodobo stabilny plugin, ktory ostane pouzitelny aj pocas priebeznych zlepseni.

## Core Value

Stabilna a spolahliva integracia, ktora korektne cita data zo `zsed.sk` a zrozumitelne ich prezentuje na Home Assistant dashboarde.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Integracia korektne parsuje dostupne relevantne data zo `zsed.sk`.
- [ ] Parser prioritizuje presnost hodnot a minimalizuje parsing chyby.
- [ ] Vytvorene entity su konzistentne a pouzitelne v Home Assistant.
- [ ] Dashboard prezentacia je zrozumitelna, prehladna a prakticka pre bezne pouzitie.
- [ ] Pri vylepseniach je mozne pridavat nove funkcie, ak podporia stabilitu a hodnotu integracie.

### Out of Scope

- (None explicitly defined yet) — scope ostava zatial otvoreny podla priebeznych potrieb projektu.

## Context

Projekt je zamerany na komunitne pouzitie ako verejne zdielany plugin.
Zdrojova funkcionalita uz existuje v aktualnych suboroch repozitara a bude sa iterativne zlepsovat.
Primarny zdroj dat je `zsed.sk`, kde parser musi udrzat vysoku presnost vystupu.
Prezentacna priorita je kvalita dashboardu v Home Assistant, nie iba technicke nacitanie dat.

## Constraints

- **Source Dependency**: Data source je `zsed.sk` — parser sa musi prisposobit strukture a moznym zmenam webu.
- **Community Quality**: Plugin je urceny pre komunitu — stabilita a predvidatelnost spravania su klucove.
- **Home Assistant UX**: Vystup musi byt dobre pouzitelny v dashboardoch — samotna dostupnost dat nestaci.
- **Incremental Delivery**: Nove funkcie sa mozu objavit pocas vylepsovania — treba ich riadit bez narusenia stability.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Prioritou parsera je presnost dat | Nekorektne hodnoty znizuju doveru a pouzitelnost integracie | — Pending |
| Prioritou prezentacie su dashboardy v Home Assistant | Koncovy uzivatel hodnotu vidi najma cez dashboard | — Pending |
| Scope zatial ostava otvoreny pre nove funkcie | Počas vylepsovania sa mozu objavit relevantne poziadavky | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-29 after initialization*
