---
phase: 5
slug: home-assistant-entity-presentation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio |
| **Config file** | `pytest.ini` |
| **Quick run command** | `python -m pytest -q tests/test_entity_presentation_contract.py` |
| **Full suite command** | `python -m pytest -q tests` |
| **Estimated runtime** | ~20-60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest -q tests/test_entity_presentation_contract.py`
- **After every plan wave:** Run `python -m pytest -q tests`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | HAPR-01, HAPR-02 | — | N/A | contract | `python -m pytest -q tests/test_entity_presentation_contract.py -k entities` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | HAPR-02, HAPR-03 | — | N/A | docs parity | `python -m pytest -q tests/test_entity_presentation_contract.py -k docs` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 2 | HAPR-01, HAPR-02, HAPR-03 | — | N/A | regression | `python -m pytest -q tests` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_entity_presentation_contract.py` — contract tests for the 3 entities and required attributes
- [ ] fixture/helper hooks for deterministic sensor/coordinator payload checks

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Advanced Mushroom + card-mod timeline recipe renders correctly | HAPR-03 | Depends on live HA dashboard rendering and optional custom cards | Open Lovelace dashboard using `EXAMPLES.md` advanced card and verify expected visuals and no template/runtime errors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
