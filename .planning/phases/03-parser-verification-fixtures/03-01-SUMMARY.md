---
phase: 03-parser-verification-fixtures
plan: 01
subsystem: testing
tags: [pytest, pytest-asyncio, parser, fixtures, offline-tests]
requires:
  - phase: 03-parser-verification-fixtures
    provides: "Phase scope, research constraints, and parser contract targets for PARS-04."
provides:
  - "Deterministic parser fixture corpus for standard and malformed HTML inputs."
  - "Pytest + pytest-asyncio baseline and parser-only test harness."
  - "Contract tests for _extract_javascript_array, _normalize_schedule, and async get_schedule."
affects: [PARS-04, parser-regression-gate, release-readiness]
tech-stack:
  added: [pytest-asyncio]
  patterns: [offline-fixture-testing, async-fetch-seam-patching, explicit-contract-assertions]
key-files:
  created:
    - pytest.ini
    - tests/conftest.py
    - tests/fixtures/parser/standard_household_business.html
    - tests/fixtures/parser/malformed_js_array.html
    - tests/fixtures/parser/missing_var_name.html
    - tests/test_parser_extract.py
    - tests/test_parser_normalize.py
    - tests/test_parser_get_schedule.py
  modified: []
key-decisions:
  - "Parser tests load parser.py directly via importlib to avoid Home Assistant runtime dependency."
  - "Async get_schedule tests patch both fetch_page and _calculate_current_tariff for full offline determinism."
patterns-established:
  - "Fixture-driven parser contracts with explicit failure semantics ([] and None)."
  - "Required-key assertions for parser API payload shape to catch downstream contract drift."
requirements-completed: [PARS-04]
duration: 50min
completed: 2026-04-29
---

# Phase 3 Plan 01: Parser Verification Fixtures Summary

**Offline parser regression gate with deterministic HTML fixtures and async seam-patched contract tests for extract, normalize, and get_schedule behavior**

## Performance

- **Duration:** 50 min
- **Started:** 2026-04-29T14:13:00Z
- **Completed:** 2026-04-29T14:55:00Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Added minimal pytest execution baseline (`pytest.ini`) and fixture loader in `tests/conftest.py`.
- Added deterministic offline fixture corpus for standard, malformed-array, and missing-variable parser scenarios.
- Added parser contract tests for extraction/normalization semantics and async API (`get_schedule`) with patched network seam.
- Verified full parser fixture suite passes via `py -m pytest tests -q` (8 passed).

## Task Commits

Each task was committed atomically:

1. **Task 1: Bootstrap parser-only test baseline and offline fixture corpus** - `8f5a09e` (chore)
2. **Task 2: Implement deterministic unit contracts for extract and normalize behavior** - `27ecb8f` (test, RED), `52c077e` (feat, GREEN)
3. **Task 3: Add async parser API contract tests with patched fetch seam** - `97e1965` (feat)

## Files Created/Modified
- `pytest.ini` - Enables pytest discovery for `tests` and async mode auto.
- `tests/conftest.py` - Provides shared HTML fixture loader fixtures.
- `tests/fixtures/parser/standard_household_business.html` - Deterministic happy-path parser input.
- `tests/fixtures/parser/malformed_js_array.html` - Deterministic malformed bracket/input failure case.
- `tests/fixtures/parser/missing_var_name.html` - Deterministic missing-variable failure case.
- `tests/test_parser_extract.py` - Contract assertions for `_extract_javascript_array` success and `[]` failure semantics.
- `tests/test_parser_normalize.py` - Contract assertions for `_normalize_schedule` NT filtering and day-bucket mapping.
- `tests/test_parser_get_schedule.py` - Async contract assertions for `get_schedule` keys, unknown-HDO `None`, and offline patched fetch.

## Decisions Made
- Loaded `parser.py` directly in tests to keep this phase parser-only and independent of Home Assistant harness dependencies.
- Stabilized time-sensitive output by patching `_calculate_current_tariff` in async API tests.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing async pytest plugin**
- **Found during:** Task 1 verification
- **Issue:** `pytest.ini` used `asyncio_mode`, but `pytest-asyncio` plugin was missing (`Unknown config option: asyncio_mode`).
- **Fix:** Installed `pytest-asyncio` in local Python environment.
- **Files modified:** none (environment dependency)
- **Verification:** `py -m pytest tests -q` passes.
- **Committed in:** N/A (environment-only)

**2. [Rule 3 - Blocking] Resolved parser import path for test-only execution**
- **Found during:** Task 2 GREEN run
- **Issue:** Direct package import required Home Assistant module and failed in parser-only environment.
- **Fix:** Loaded parser via `importlib` and inserted parser directory in `sys.path` for `time_semantics` resolution.
- **Files modified:** `tests/test_parser_extract.py`, `tests/test_parser_normalize.py`
- **Verification:** `py -m pytest tests/test_parser_extract.py tests/test_parser_normalize.py -q -x` passed.
- **Committed in:** `52c077e`

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes were required to keep tests runnable and deterministic without expanding scope beyond parser verification.

## Issues Encountered
- `py -m pytest --collect-only -q` returns exit code 5 when no tests exist yet; after task test files were added, collection/execution gates became meaningful and green.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `PARS-04` parser fixture verification gate is now executable and deterministic.
- Ready to proceed with broader reliability/release phases while reusing parser contract suite as regression guardrail.

## Self-Check: PASSED
