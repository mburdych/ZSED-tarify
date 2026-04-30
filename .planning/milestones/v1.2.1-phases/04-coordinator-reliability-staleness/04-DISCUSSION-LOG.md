# Phase 4: Coordinator Reliability & Staleness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 04-coordinator-reliability-staleness
**Areas discussed:** Degraded mode behavior

---

## Degraded mode behavior

### Q1: Ako dlho mozeme povazovat cache za pouzitelnu bez uspesneho refreshu?

| Option | Description | Selected |
|--------|-------------|----------|
| cache_age_warn24h | Pouzit stare data, po 24h warning stale mode | |
| cache_age_hard12h | Po 12h prestat publikovat schedule ako validne | |
| cache_age_no_limit | Vzdy pouzit posledne uspesne data, kym nepridu nove | ✓ |

**User's choice:** cache_age_no_limit  
**Notes:** Dostupnost je priorita aj pri dlhsom vypadku.

---

### Q2: Kde ma byt stale stav viditelny?

| Option | Description | Selected |
|--------|-------------|----------|
| attrs_only | Len atributy existujucich entit (stale flag + age), bez novej entity | ✓ |
| new_sensor | Samostatny stale sensor + atributy | |
| logs_only | Len logy, bez user-visible poli | |

**User's choice:** attrs_only  
**Notes:** Preferovane je minimalne rozsirenie bez novych entit.

---

### Q3: Co po obnove zdroja?

| Option | Description | Selected |
|--------|-------------|----------|
| auto_recover_clear_flags | Po prvom uspesnom refreshi clear stale flag + reset age | ✓ |
| manual_ack | Stale stav drzat do manualneho potvrdenia | |
| grace_period_clear | Clear az po X po sebe uspesnych refreshoch | |

**User's choice:** auto_recover_clear_flags  
**Notes:** Recovery ma byt automaticky, bez manualnych krokov.

---

## Claude's Discretion

- Presne nazvy staleness atributov.
- Detailna retry/backoff implementacna matica v medziach RELI-03/04.

## Deferred Ideas

- Samostatny dedicated staleness sensor.
- Manual acknowledgement flow pri recoveri.
