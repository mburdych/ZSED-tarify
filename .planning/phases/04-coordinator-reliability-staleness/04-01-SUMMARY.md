---
phase: 04-coordinator-reliability-staleness
plan: 01
subsystem: reliability
tags: [home-assistant, coordinator, retry-backoff, stale-metadata, pytest]
requires:
  - phase: 03-parser-verification-fixtures
    provides: parser schedule contract and fixture-backed baseline tests
provides:
  - Coordinator-owned bounded retry/backoff progression for repeated refresh failures
  - Explicit stale metadata fields on coordinator payloads for cached degraded mode
  - Async reliability contract tests covering failure progression and recovery reset
affects: [phase-04-plan-02, sensor-attributes, coordinator-refresh]
tech-stack:
  added: []
  patterns: [coordinator-owned reliability envelope, bounded exponential backoff]
key-files:
  created: [tests/test_coordinator_reliability.py]
  modified: [custom_components/zse_hdo/const.py, custom_components/zse_hdo/coordinator.py]
key-decisions:
  - "Backoff enforcement stays inside coordinator by gating fetch attempts until next_retry_at."
  - "Cached fallback remains unlimited but always carries explicit stale metadata keys."
patterns-established:
  - "Reliability metadata is emitted in every coordinator payload path (fresh and stale)."
  - "Scheduled mode uses one-shot retry timer while interval mode is throttled via next_retry_at."
requirements-completed: [RELI-01, RELI-02, RELI-03]
duration: 6min
completed: 2026-04-29
---

# Phase 04 Plan 01: Coordinator Reliability Contract Summary

**Coordinator refresh now applies bounded backoff with explicit stale/failure metadata while preserving unlimited cached fallback availability.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-29T14:49:00Z
- **Completed:** 2026-04-29T14:55:41Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Added async reliability tests that define retry/backoff, stale fallback, and recovery reset behavior.
- Implemented coordinator-owned reliability state (`consecutive_failures`, `next_retry_at`, stale timestamps) in refresh flow.
- Added bounded retry constants and scheduled-mode one-shot retry timer while keeping cached fallback unlimited.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add coordinator reliability contract tests before implementation** - `5f8b5ae` (test)
2. **Task 2: Implement bounded retry/backoff and reliability metadata in coordinator** - `0ef9236` (feat)

## Files Created/Modified
- `tests/test_coordinator_reliability.py` - New coordinator reliability contract tests (RED/GREEN coverage).
- `custom_components/zse_hdo/const.py` - Backoff bounds and multiplier constants.
- `custom_components/zse_hdo/coordinator.py` - Reliability state machine, stale metadata envelope, and retry scheduling.

## Decisions Made
- Kept reliability ownership entirely in coordinator payload construction to preserve RELI-01 boundaries.
- Applied fetch-throttling via `next_retry_at` so interval mode avoids repeated source hammering during outages.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Coordinator now emits deterministic reliability fields needed by downstream entity propagation work (Plan 04-02).
- Retry/backoff and stale semantics are covered by targeted tests and full suite regression gate.

## Self-Check: PASSED

- Verified summary file exists at `.planning/phases/04-coordinator-reliability-staleness/04-01-SUMMARY.md`.
- Verified task commits `5f8b5ae` and `0ef9236` exist in git history.

---
*Phase: 04-coordinator-reliability-staleness*
*Completed: 2026-04-29*
