---
phase: 4
slug: coordinator-reliability-staleness
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio (existing in repo after Phase 3) |
| **Config file** | `pytest.ini` |
| **Quick run command** | `python -m pytest -q tests/test_coordinator_reliability.py` |
| **Full suite command** | `python -m pytest -q tests` |
| **Estimated runtime** | ~20-60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest -q tests/test_coordinator_reliability.py`
- **After every plan wave:** Run `python -m pytest -q tests`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | RELI-03 | — | N/A | unit/async | `python -m pytest -q tests/test_coordinator_reliability.py -k backoff` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | RELI-04 | — | N/A | unit | `python -m pytest -q tests/test_coordinator_reliability.py -k staleness` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | RELI-01, RELI-02, RELI-03, RELI-04 | — | N/A | integration-lite | `python -m pytest -q tests/test_coordinator_reliability.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_coordinator_reliability.py` — retry/backoff + stale metadata + recovery behavior assertions
- [ ] test fixtures/mocks for coordinator update failures and success recovery path

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| HA entity cards visibly show stale metadata in real runtime UI | RELI-04 | UI rendering and perceived clarity is HA-dashboard dependent | Run HA dev instance, trigger fetch failures, inspect attributes on tariff/next-switch/today-schedule entities |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
