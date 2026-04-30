---
phase: 04-coordinator-reliability-staleness
plan: 02
subsystem: reliability
tags: [home-assistant, coordinator, sensor-attributes, stale-metadata, pytest]
requires:
  - phase: 04-coordinator-reliability-staleness
    provides: coordinator retry/backoff metadata envelope and recovery reset state
provides:
  - Existing tariff, next-switch, and today-schedule entities now expose coordinator stale metadata directly in attributes
  - Recovery payload semantics are validated at entity level (stale flags/counters clear on first successful refresh)
  - Regression contract tests for stale consistency across all existing entities
affects: [entity-attributes, dashboards, automations, phase-04-summary]
tech-stack:
  added: []
  patterns: [coordinator-owned reliability projection, entity attribute contract testing]
key-files:
  created: [tests/test_sensor_staleness_attrs.py]
  modified: [custom_components/zse_hdo/sensor.py]
key-decisions:
  - "Reliability metadata remains coordinator-owned and is projected into all existing entities through a shared helper."
  - "Next-switch sensor keeps backward-compatible behavior while still surfacing stale metadata even when switch details are unavailable."
patterns-established:
  - "All existing entity extra_state_attributes include the same stale contract keys."
  - "Entity-level recovery behavior is asserted from coordinator payload transitions without network coupling."
requirements-completed: [RELI-04, RELI-02]
duration: 9min
completed: 2026-04-29
---

# Phase 04 Plan 02: Coordinator Staleness Entity Projection Summary

**Coordinator reliability metadata now flows into all three existing entities so stale/degraded state is user-visible and automatically clears on recovery.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-29T14:55:00Z
- **Completed:** 2026-04-29T15:03:52Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added TDD contract tests for stale metadata visibility, cross-entity consistency, and recovery reset behavior.
- Wired stale metadata keys into tariff, next-switch, and today-schedule `extra_state_attributes`.
- Verified coordinator recovery reset remains reflected in entity attributes and full test suite stays green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add entity-level staleness attribute contract tests** - `0de4827` (test)
2. **Task 2: Wire reliability metadata into existing sensor attributes and finalize recovery reset path** - `3e1f194` (feat)

## Files Created/Modified
- `tests/test_sensor_staleness_attrs.py` - New contract tests covering stale visibility, consistency, and reset semantics.
- `custom_components/zse_hdo/sensor.py` - Added shared reliability projection and merged reliability keys into all existing sensor attributes.

## Decisions Made
- Kept stale-state ownership in coordinator payload fields and only projected them at entity level, preserving RELI-01 boundaries.
- Reused a single helper for reliability keys so all entities expose an identical stale metadata contract.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Existing entities now expose stale/fresh state directly for dashboards and automations.
- Recovery clear semantics are covered by entity-level tests and coordinator reliability regression tests.

## Self-Check: PASSED

- Verified summary file exists at `.planning/phases/04-coordinator-reliability-staleness/04-02-SUMMARY.md`.
- Verified task commits `0de4827` and `3e1f194` exist in git history.

---
*Phase: 04-coordinator-reliability-staleness*
*Completed: 2026-04-29*
