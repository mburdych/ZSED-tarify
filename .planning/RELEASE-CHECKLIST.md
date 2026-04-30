# Release Checklist (v1.x)

Repeatable pre-release loop for `ZSE HDO Live`.

## 1) Version and metadata sync

- [x] Bump `custom_components/zse_hdo/manifest.json` `version`
- [x] Confirm `hacs.json` remains compatible (domain/name/min HA/repo links)
- [x] Ensure branch is clean and tests are passing before tag/release

## 2) Automated verification gate

- [x] Run full suite: `py -m pytest -q tests`
- [x] Resolve any failing contract tests before continuing
- [x] Verify no new lint issues in touched files

## 3) Manual HA smoke-test gate

- [x] Install/update integration in clean HA dev instance
- [x] Add integration via UI (`Settings -> Devices & Services`)
- [x] Confirm baseline entities render correctly:
  - `binary_sensor.zse_hdo_<N>_tariff`
  - `sensor.zse_hdo_<N>_next_switch`
  - `sensor.zse_hdo_<N>_today_schedule`
  - `sensor.zse_hdo_<N>_low_remaining`
- [x] Validate one degraded/failure path markers are visible (`diagnostic_error_*`)
- [x] Validate schedule-change marker path (`schedule_changed`, `schedule_change_at`)

## 4) Docs and examples sync

- [x] Update `README.md` changelog with new version/date and key changes
- [x] Verify `README.md` entity attributes match live contract
- [x] Verify `EXAMPLES.md` snippets reference real entity IDs/attributes
- [x] Keep `AGENTS.md` and `CLAUDE.md` release/testing guidance aligned

## 5) Release publish sequence

- [x] Commit release metadata/docs changes
- [x] Create and push release tag matching `manifest.json` version
- [x] Publish GitHub release notes (same core points as README changelog)
- [x] Post-release sanity: fresh install path + one update path still work

## 6) Post-release bookkeeping

- [x] Update `.planning/ROADMAP.md` and `.planning/STATE.md` with release status
- [x] Mark validated requirements for released scope in `.planning/REQUIREMENTS.md`
- [x] Capture deferred manual checks in latest phase summary if any
