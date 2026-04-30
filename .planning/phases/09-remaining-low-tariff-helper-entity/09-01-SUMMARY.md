# Phase 09-01 Summary: Remaining Low Tariff Helper Entity

## Outcome

Implemented VADD-01 helper entity for remaining low-tariff window.

- Added `sensor.zse_hdo_<N>_low_remaining` in `sensor.py`.
- Exposed helper attributes:
  - `remaining_minutes`
  - `period_end`
  - `is_low_tariff_now`
- Preserved reliability/diagnostic metadata passthrough for consistency.

## Test Coverage

- Added `tests/test_low_tariff_remaining_sensor.py` for boundary behavior:
  - active workday low period
  - outside low period
  - midnight-crossing low period
  - weekend schedule branch
- Extended `tests/test_entity_presentation_contract.py` for new entity contract.
- Updated `tests/test_parser_extract.py` to align with parser parse-error contract.
- Full suite green: `py -m pytest -q tests`.

## Documentation

- Updated `README.md` entity list and baseline examples with helper sensor.
- Updated `EXAMPLES.md` baseline and template-card examples for helper usage.

## Human Checkpoint Status

Manual dashboard readability verification for helper behavior remains pending.

- Status: **Deferred**
- Follow-up trigger: run before Phase 11 release-loop checkpoint or before `v1.2.0` release.
