# Milestones

## v1.2.1 Patch & Blueprint Expansion (Shipped: 2026-04-30)

**Phases completed:** 12 phases archived, 15 plans, 18 tasks
**Git range:** `42eb7f8` → `545ded6` (post-v1.2.0 → v1.2.1 release)
**Tag:** `v1.2.1`

**Key accomplishments:**

- **STAB-01** — Stabilization sweep for low-remaining boundary semantics (Phase 12).
- **VADD-02** — Home Assistant blueprint automation pack for common HDO flows (Phase 13).
- **DIAG-02** — Diagnostics UX polish: severity markers + operator-friendly guidance text (Phase 14).
- **DOCS-01** — Docs hygiene + planning artifact consistency for patch release (Phase 15).
- **RELEASE-LOOP-01 (continued)** — Repeatable release checklist exercised end-to-end on a patch.

**Known deferred items at close:** 2 (legacy v1.1.0 verification flags on Phases 02/04 — see STATE.md Deferred Items)

---

## v1.2.0 Diagnostics + Value Add (Shipped: 2026-04-30)

**Key deliveries:**
- CONF-03: diagnostic signal separation (fetch / parse / tariff markers).
- VADD-01: remaining low-tariff helper sensor.
- VADD-03: schedule-change notification hooks.
- RELEASE-LOOP-01: codified release loop checklist workflow.

---

## v1.1.0 Reliability + Fixtures (Shipped: 2026-04-29)

**Key deliveries:**
- Async fetch + parser contract (PARS-01..04).
- Tariff time semantics with HA `dt_util` and shared helper (TIME-01..03, TZ-01, CODE-01).
- Coordinator reliability + staleness propagation (RELI-01..04).
- HA entity presentation contract + dashboard recipes (HAPR-01..03).
- Config / options flow (CONF-01, CONF-02).
- Release readiness checkpoint (RELEASE-01..04).
