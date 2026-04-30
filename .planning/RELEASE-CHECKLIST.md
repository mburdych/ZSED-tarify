# Release Checklist (v1.x)

Repeatable pre-release loop for `ZSE HDO Live`.

## 1) Version and metadata sync

- [ ] Bump `custom_components/zse_hdo/manifest.json` `version`
- [ ] Confirm `hacs.json` remains compatible (domain/name/min HA/repo links)
- [ ] Ensure branch is clean and tests are passing before tag/release

## 2) Automated verification gate

- [ ] Run full suite: `py -m pytest -q tests`
- [ ] Resolve any failing contract tests before continuing
- [ ] Verify no new lint issues in touched files

## 3) Manual HA smoke-test gate

- [ ] Install/update integration in clean HA dev instance
- [ ] Add integration via UI (`Settings -> Devices & Services`)
- [ ] Confirm baseline entities render correctly:
  - `binary_sensor.zse_hdo_<N>_tariff`
  - `sensor.zse_hdo_<N>_next_switch`
  - `sensor.zse_hdo_<N>_today_schedule`
  - `sensor.zse_hdo_<N>_low_remaining`
- [ ] Validate one degraded/failure path markers are visible (`diagnostic_error_*`)
- [ ] Validate schedule-change marker path (`schedule_changed`, `schedule_change_at`)

## 4) Docs and examples sync

- [ ] Update `README.md` changelog with new version/date and key changes
- [ ] Verify `README.md` entity attributes match live contract
- [ ] Verify `EXAMPLES.md` snippets reference real entity IDs/attributes
- [ ] Keep `AGENTS.md` and `CLAUDE.md` release/testing guidance aligned

## 5) Release publish sequence

- [ ] Commit release metadata/docs changes
- [ ] Create and push release tag matching `manifest.json` version
- [ ] Publish GitHub release notes (same core points as README changelog)
- [ ] Post-release sanity: fresh install path + one update path still work

## 6) Post-release bookkeeping

- [ ] Update `.planning/ROADMAP.md` and `.planning/STATE.md` with release status
- [ ] Mark validated requirements for released scope in `.planning/REQUIREMENTS.md`
- [ ] Capture deferred manual checks in latest phase summary if any
