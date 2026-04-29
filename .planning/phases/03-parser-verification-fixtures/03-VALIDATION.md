---
phase: 3
slug: parser-verification-fixtures
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio |
| **Config file** | `pytest.ini` (to be added in Wave 0) |
| **Quick run command** | `python -m pytest -q tests/test_parser.py` |
| **Full suite command** | `python -m pytest -q` |
| **Estimated runtime** | ~20-40 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest -q tests/test_parser.py`
- **After every plan wave:** Run `python -m pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 45 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | PARS-04 | — | N/A | setup | `python -m pytest --version` | ✅ | ⬜ pending |
| 03-01-02 | 01 | 1 | PARS-04 | — | N/A | unit/async | `python -m pytest -q tests/test_parser.py` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | PARS-04 | — | N/A | regression | `python -m pytest -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_parser.py` — fixture-based parser test coverage for standard and problematic inputs
- [ ] `tests/fixtures/*.html` — deterministic HTML fixtures for parser extraction and normalization cases
- [ ] `pytest.ini` — baseline test discovery/options for parser-only suite

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 45s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
