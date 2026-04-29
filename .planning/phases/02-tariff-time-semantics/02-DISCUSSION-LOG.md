# Phase 2: Tariff Time Semantics - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 2-Tariff Time Semantics
**Areas discussed:** Time source standard

---

## Time source standard

| Option | Description | Selected |
|--------|-------------|----------|
| Use `homeassistant.util.dt` everywhere | parser + sensors + helpers all read time via HA utilities | ✓ |
| Use HA dt_util only in runtime sensors/coordinator | parser timestamps remain stdlib datetime | |
| Keep current mix | continue with mixed stdlib/HA time usage | |

**User's choice:** Use `homeassistant.util.dt` everywhere.
**Notes:** This is the canonical source of "now" for all tariff calculations.

| Option | Description | Selected |
|--------|-------------|----------|
| HA local wall-clock times | interpret ZSE schedule as local HA time and compare locally | ✓ |
| UTC conversion pipeline | convert schedule and runtime to UTC-aware datetimes first | |
| Fixed offset | manual fixed timezone offset strategy | |

**User's choice:** Treat schedule as HA local wall-clock time.
**Notes:** Keeps behavior aligned with user-local Home Assistant timezone semantics.

| Option | Description | Selected |
|--------|-------------|----------|
| Shared helper module/function | one reusable evaluator for parser + sensors | ✓ |
| Sensor-owned logic | keep main logic in sensors and adapt parser around it | |
| Parser-owned logic | keep main logic in parser and call it from sensors | |

**User's choice:** Create one shared helper consumed by parser + sensors.
**Notes:** Main goal is removing duplicated midnight/tariff decision logic.

| Option | Description | Selected |
|--------|-------------|----------|
| Follow HA local DST rules via dt_util | preserve current schedule semantics while using HA time stack | ✓ |
| Add explicit DST branching | hand-crafted DST-specific code paths | |
| Defer DST specifics | leave exact strategy to later discretion | |

**User's choice:** Follow HA local rules via `dt_util`.
**Notes:** DST handling should not change the existing user-visible tariff schedule semantics.

---

## Claude's Discretion

- Naming and placement of shared helper symbols/module for tariff evaluation.

## Deferred Ideas

- None.
