---
phase: 2
slug: tariff-time-semantics
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | other (manual Home Assistant integration checks + parser smoke run) |
| **Config file** | none — relies on integration runtime environment |
| **Quick run command** | `python custom_components/zse_hdo/parser.py` |
| **Full suite command** | `python custom_components/zse_hdo/parser.py` + Home Assistant manual smoke flow |
| **Estimated runtime** | ~60 seconds parser smoke, plus HA restart/manual checks |

---

## Sampling Rate

- **After every task commit:** Run `python custom_components/zse_hdo/parser.py`
- **After every plan wave:** Re-run parser smoke and verify tariff state/next switch in a HA dev instance
- **Before `/gsd-verify-work`:** Parser smoke and manual HA checks must pass
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | TIME-01 | — | N/A | smoke | `python custom_components/zse_hdo/parser.py` | ✅ | ⬜ pending |
| 02-01-02 | 01 | 1 | TIME-02 | — | N/A | smoke | `python custom_components/zse_hdo/parser.py` | ✅ | ⬜ pending |
| 02-01-03 | 01 | 1 | TIME-03 | — | N/A | smoke | `python custom_components/zse_hdo/parser.py` | ✅ | ⬜ pending |
| 02-02-01 | 02 | 1 | TZ-01 | — | N/A | manual+smoke | `python -m py_compile custom_components/zse_hdo/parser.py custom_components/zse_hdo/sensor.py custom_components/zse_hdo/time_semantics.py && rg "_calculate_current_tariff|_get_next_switch|datetime\.now\(" custom_components/zse_hdo && python custom_components/zse_hdo/parser.py` | ✅ | ✅ green |
| 02-02-02 | 02 | 1 | CODE-01 | — | N/A | manual+smoke | `python -m py_compile custom_components/zse_hdo/parser.py custom_components/zse_hdo/sensor.py custom_components/zse_hdo/time_semantics.py && rg "_calculate_current_tariff|_get_next_switch|datetime\.now\(" custom_components/zse_hdo && python custom_components/zse_hdo/parser.py` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/` automation scaffold — deferred (project currently has no automated suite)
- [ ] HA dev instance with `custom_components/zse_hdo/` loaded for runtime validation

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Entity `is_on` flips exactly on period boundaries using HA timezone | TZ-01 | Requires live HA clock/timezone context | Configure integration, observe transitions around known boundary times and compare with schedule |
| Next-switch attribute remains correct across midnight and weekday/weekend crossover | TIME-02, TIME-03 | Needs runtime wall-clock progression semantics | Validate just before and after midnight in HA and compare with expected next interval |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or explicit manual fallback
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 300s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
