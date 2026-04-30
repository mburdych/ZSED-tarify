---
phase: 04-coordinator-reliability-staleness
verified: 2026-04-29T15:07:53.166976Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
human_verification:
  - test: "HA outage degraded-mode visibility"
    expected: "Entities remain available and expose stale metadata with increasing age during source outage."
    why_human: "Requires live Home Assistant runtime plus real source/network failure simulation."
  - test: "HA recovery stale reset"
    expected: "On first successful refresh after outage, stale fields clear on all existing entities without manual intervention."
    why_human: "Requires end-to-end coordinator refresh lifecycle in Home Assistant runtime."
---

# Phase 4: Coordinator Reliability & Staleness Verification Report

**Phase Goal:** Refresh politika a fallback mechanizmy zabezpecia stabilny chod entit aj pocas docasnych problemov zdroja, s explicitne citatelnym vekom dat.
**Verified:** 2026-04-29T15:07:53.166976Z
**Status:** human_needed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Coordinator remains single owner of refresh/cache/reliability state (RELI-01). | ✓ VERIFIED | `custom_components/zse_hdo/__init__.py` wires one `ZSEHDOCoordinator`; entities consume `coordinator.data`; reliability fields are authored in `custom_components/zse_hdo/coordinator.py`. |
| 2 | Cached data stays available during source outages with explicit degraded metadata (RELI-02). | ✓ VERIFIED | Failure path in `_async_update_data` returns cached payload when `_last_known_data` exists and enriches `is_stale`, `stale_for_s`, `consecutive_failures`, timestamps, and `next_retry_at`. |
| 3 | Repeated runtime failures use explicit bounded retry/backoff (RELI-03). | ✓ VERIFIED | Backoff constants in `custom_components/zse_hdo/const.py`; coordinator computes bounded delay via `_compute_retry_delay`, gates interval refresh using `_next_retry_at`, and schedules one-shot retry for scheduled mode. |
| 4 | Existing entities expose readable stale age/status metadata (RELI-04). | ✓ VERIFIED | All three entities merge `_reliability_attrs(...)` in `extra_state_attributes` in `custom_components/zse_hdo/sensor.py`; tests assert fields are present and consistent. |
| 5 | First successful refresh clears stale state automatically (D-05 contract). | ✓ VERIFIED | Success path resets `_consecutive_failures`, `_next_retry_at`, `_last_error_at`, and emits fresh metadata; covered by recovery assertions in both coordinator and sensor reliability tests. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `custom_components/zse_hdo/const.py` | Backoff tuning constants with safe bounds | ✓ VERIFIED | Defines `RETRY_BACKOFF_MIN_SECONDS`, `RETRY_BACKOFF_MAX_SECONDS`, `RETRY_BACKOFF_MULTIPLIER`; used by coordinator retry calculation. |
| `custom_components/zse_hdo/coordinator.py` | Reliability state machine, fallback metadata, retry scheduling | ✓ VERIFIED | Substantive implementation of retry gating, scheduled retry timer, stale metadata enrichment, and reset-on-success behavior. |
| `custom_components/zse_hdo/sensor.py` | Unified stale metadata projection on existing entities | ✓ VERIFIED | `_reliability_attrs` helper is reused by tariff, next-switch, and today-schedule entities. |
| `tests/test_coordinator_reliability.py` | Regression tests for retry/backoff, stale fallback, and recovery reset | ✓ VERIFIED | 3 focused async contract tests passed (`3 passed`). |
| `tests/test_sensor_staleness_attrs.py` | Regression tests for stale attribute exposure and recovery reset | ✓ VERIFIED | 5 contract tests passed (`5 passed`). |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `custom_components/zse_hdo/coordinator.py` | `UpdateFailed`/retry lane | `UpdateFailed(..., retry_after=...)` + `_schedule_retry_update` | ✓ WIRED | Initial no-cache failure raises `UpdateFailed` with retry hint; scheduled mode adds one-shot retry callback. |
| `custom_components/zse_hdo/coordinator.py` | `_last_known_data` fallback | stale-enriched fallback return path | ✓ WIRED | On fetch error with cache, coordinator returns enriched cached payload and keeps entities available. |
| `custom_components/zse_hdo/coordinator.py` | `custom_components/zse_hdo/sensor.py` | coordinator reliability keys projected into attrs | ✓ WIRED | Sensor `_reliability_attrs` maps coordinator payload keys directly in all entities. |
| `tests/test_coordinator_reliability.py` | `custom_components/zse_hdo/coordinator.py` | assertions on failure/stale/retry fields | ✓ WIRED | Tests validate `consecutive_failures`, `is_stale`, `stale_for_s`, `next_retry_at`, and reset semantics. |
| `tests/test_sensor_staleness_attrs.py` | `custom_components/zse_hdo/sensor.py` | `extra_state_attributes` contract assertions | ✓ WIRED | Tests cover stale field presence, cross-entity consistency, and recovery reset. |
| `custom_components/zse_hdo/sensor.py` | existing entity unique IDs | attribute-only extension | ✓ WIRED | Unique IDs remain `zse_hdo_<n>_(tariff|next_switch|today_schedule)`; no new staleness platform entity added. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `custom_components/zse_hdo/coordinator.py` | `schedule` + reliability fields | `await parser.get_schedule(...)` + runtime failure/success state | Yes | ✓ FLOWING |
| `custom_components/zse_hdo/sensor.py` | `self.coordinator.data` in entity attributes | Coordinator payload from `hass.data[DOMAIN][entry_id]["coordinator"]` wiring in `__init__.py` | Yes | ✓ FLOWING |
| `tests/test_sensor_staleness_attrs.py` | attribute contract snapshots | Sensor `extra_state_attributes` projection over coordinator payloads | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Coordinator reliability contract | `py -m pytest tests/test_coordinator_reliability.py -q -x` | `3 passed in 0.10s` | ✓ PASS |
| Entity stale-attribute contract | `py -m pytest tests/test_sensor_staleness_attrs.py -q -x` | `5 passed in 0.11s` | ✓ PASS |
| Combined phase gate | `py -m pytest tests/test_sensor_staleness_attrs.py tests/test_coordinator_reliability.py -q -x` | `8 passed in 0.03s` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| RELI-01 | `04-01-PLAN.md` | Coordinator is single source of refresh/cache logic for entities. | ✓ SATISFIED | Coordinator created once in `__init__.py`; sensors are `CoordinatorEntity` consumers; reliability state is emitted by coordinator. |
| RELI-02 | `04-01-PLAN.md`, `04-02-PLAN.md` | Cached last successful data is used during temporary source failure. | ✓ SATISFIED | `_last_known_data` fallback return path in coordinator plus stale metadata projection to entities. |
| RELI-03 | `04-01-PLAN.md` | Explicit retry/backoff for repeated failures. | ✓ SATISFIED | Bounded backoff computation, `_next_retry_at` throttling, scheduled retry timer, and passing regression tests. |
| RELI-04 | `04-02-PLAN.md` | Explicit user-visible staleness age/status as attribute/sensor. | ✓ SATISFIED | Existing entities expose stale fields in `extra_state_attributes`; tests validate values and consistency. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| N/A | N/A | No TODO/FIXME/placeholder or empty-stub anti-patterns detected in verified phase files. | ℹ️ Info | No blocker/warning anti-patterns found for phase goal achievement. |

### Human Verification Required

### 1. Live HA degraded-mode behavior

**Test:** In a Home Assistant dev instance, force source fetch failures after one successful refresh.
**Expected:** Entities remain available, `is_stale=true`, and `stale_for_s` grows while outage persists.
**Why human:** Requires real HA runtime scheduling + integration execution against live network behavior.

### 2. Live HA recovery transition

**Test:** Restore source availability after degraded mode and wait for next successful refresh.
**Expected:** `is_stale=false`, `stale_for_s=0`, `consecutive_failures=0`, and retry metadata clears automatically on all existing entities.
**Why human:** Requires end-to-end runtime refresh/recovery transitions that unit tests cannot fully replicate.

### Gaps Summary

No code-level gaps were found against phase must-haves, artifacts, key links, or requirement IDs (`RELI-01`..`RELI-04`). Remaining work is runtime human validation in Home Assistant.

---

_Verified: 2026-04-29T15:07:53.166976Z_
_Verifier: Claude (gsd-verifier)_
