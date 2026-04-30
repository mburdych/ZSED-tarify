# Phase 08-01 Summary: Diagnostic Signal Separation

## Outcome

Implemented CONF-03 diagnostic signal separation in code and tests.

- Added explicit diagnostic error typing in parser (`fetch`, `parse`, `tariff_logic` paths).
- Added coordinator-level diagnostic marker classification and payload fields:
  - `diagnostic_error_source`
  - `diagnostic_error_code`
  - `diagnostic_error_at`
- Propagated diagnostic markers to all existing entity attributes.
- Added regression tests for source separation and marker projection.

## Verification

- Automated: `py -m pytest -q tests/test_diagnostic_signal_separation.py tests/test_sensor_staleness_attrs.py tests/test_coordinator_reliability.py`
- Result: passing

## Human Checkpoint Status

Manual Home Assistant readability verification is deferred by user decision.

- Status: **Deferred**
- Scope deferred: log readability and in-HA marker inspection during forced failure simulation.
- Follow-up trigger: run before next release checkpoint (Phase 11) or at latest before `v1.2.0` publish.
