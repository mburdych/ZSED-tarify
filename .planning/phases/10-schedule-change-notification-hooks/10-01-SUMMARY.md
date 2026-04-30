# Phase 10-01 Summary: Schedule Change Notification Hooks

## Outcome

Implemented VADD-03 schedule-change signaling in coordinator payload and entity attributes.

- Added schedule fingerprint detection in `coordinator.py`.
- Added payload fields:
  - `schedule_changed`
  - `schedule_change_at`
- Exposed these fields through all sensor entity attributes.

## Test Coverage

- Added `tests/test_schedule_change_signal.py` for change/no-change detection behavior.
- Extended entity contract coverage to include new schedule-change fields.
- Full suite green: `py -m pytest -q tests`.

## Docs

- Updated `README.md` attribute lists with schedule-change fields.
- Added `EXAMPLES.md` automation example for change-triggered notification.

## Human Checkpoint Status

Manual in-HA notification flow validation is pending.

- Status: **Deferred**
- Follow-up trigger: verify before release-loop checkpoint (Phase 11).
