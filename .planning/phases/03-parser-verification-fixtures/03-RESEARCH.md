# Phase 03: parser-verification-fixtures - Research

**Researched:** 2026-04-29  
**Domain:** Parser fixture verification for Home Assistant custom integration  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Test runner and scope
- **D-01:** Baseline test stack pre Phase 3 bude minimalny `pytest + pytest-asyncio`.
- **D-02:** V tejto faze sa testuje parser layer, bez `pytest-homeassistant-custom-component` harnessu.
- **D-03:** Parser testy budu bez siete, cisto z lokalnych HTML fixtures (deterministicke vstupy).

### Definition of done for PARS-04
- **D-04:** Minimum pre splnenie `PARS-04` su klucove fixture pripady + fail pri regresii parser output shape.
- **D-05:** Sirenie na rozsiahlu corner-case maticu je mozne neskor, ale nie je podmienkou tejto fazy.

### Claude's Discretion
- Presny naming test suborov, fixture suborov a helper funkcii.
- Presne rozdelenie klucovych fixture pripadov do konkretnej test modulovej struktury.

### Deferred Ideas (OUT OF SCOPE)
- Rozsiahla corner-case matica parser vstupov nad minimum pre `PARS-04`.
- Home Assistant test harness (`pytest-homeassistant-custom-component`) pre neskorsiu fazu mimo scope Phase 3.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PARS-04 | Parser je overeny fixture testami pre bezne aj hranicne varianty vstupu. [VERIFIED: `.planning/REQUIREMENTS.md`] | Fixture-only offline parser tests, deterministic HTML inputs, and explicit failure contracts for parse regressions and output shape. [VERIFIED: `.planning/ROADMAP.md`, `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`] |
</phase_requirements>

## Summary

Phase 3 should add a minimal, parser-only pytest layer with deterministic local fixtures and no Home Assistant harness, exactly matching locked decisions D-01..D-03. [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`] The repository currently has no test runner, no `tests/` directory, and no pytest configuration, so Wave 0 must establish a tiny baseline before parser cases are implemented. [VERIFIED: `.planning/codebase/TESTING.md`]

The parser surface naturally splits into pure deterministic units (`_extract_javascript_array`, `_normalize_schedule`) and async entry points (`get_schedule`, `get_all_hdo_numbers`) that should be network-isolated by patching `fetch_page()` return values. [VERIFIED: `custom_components/zse_hdo/parser.py`] For deterministic failure contracts, tests should assert explicit return semantics already present in code: `[]` for malformed/missing JS arrays, `None` for missing HDO code, and stable key-shape for successful schedule payloads. [VERIFIED: `custom_components/zse_hdo/parser.py`]

`pytest` and `pytest-asyncio` are current, actively maintained options and align with the requested minimal stack. [CITED: https://docs.pytest.org/en/stable/, https://pytest-asyncio.readthedocs.io/en/stable/] Latest versions verified today are `pytest 9.0.3` (uploaded 2026-04-07) and `pytest-asyncio 1.3.0` (uploaded 2025-11-10). [VERIFIED: PyPI JSON API]

**Primary recommendation:** Implement parser fixture testing in two layers: pure helper tests first, then async parser API tests using patched `fetch_page`, with output-shape assertions as the regression gate for `PARS-04`. [VERIFIED: `custom_components/zse_hdo/parser.py`, `.planning/ROADMAP.md`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Fixture corpus management | Test layer (`tests/fixtures`) | Filesystem | Deterministic parser inputs must come from versioned local HTML files, not network. [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`] |
| JavaScript array extraction correctness | Parser domain logic | Test assertions | `_extract_javascript_array` is parser-owned logic; tests validate behavior contracts. [VERIFIED: `custom_components/zse_hdo/parser.py`] |
| Schedule normalization correctness | Parser domain logic | Test assertions | `_normalize_schedule` transforms source intervals into workday/weekend low-tariff model. [VERIFIED: `custom_components/zse_hdo/parser.py`] |
| Async entry-point verification (`get_schedule`) | Parser async API | pytest-asyncio runner | Async behavior belongs in parser methods; pytest-asyncio provides coroutine execution. [CITED: https://pytest-asyncio.readthedocs.io/en/stable/] |
| Network isolation | Test doubles/mocks | Parser API seam (`fetch_page`) | Patching `fetch_page` keeps tests deterministic and offline as required. [VERIFIED: `custom_components/zse_hdo/parser.py`, `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`] |

## Project Constraints (from .cursor/rules/)

No `.cursor/rules/` directory exists in this repository, so there are no additional project-local rule files to enforce beyond existing repository guidance docs. [VERIFIED: filesystem scan]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.3 | Test discovery, assertions, parametrization, fixtures | Canonical Python test runner with mature fixture/parametrize model and rich ecosystem. [CITED: https://docs.pytest.org/en/stable/] [VERIFIED: PyPI JSON API] |
| pytest-asyncio | 1.3.0 | Native async test execution via `@pytest.mark.asyncio` and asyncio config | Direct support for coroutine tests, matching parser async methods. [CITED: https://pytest-asyncio.readthedocs.io/en/stable/] [VERIFIED: PyPI JSON API] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest.mock` (stdlib) | Python 3.14 stdlib | Patch parser I/O seams (`fetch_page`) and use `AsyncMock` where needed | Use for deterministic, no-network async API tests. [CITED: https://docs.python.org/3/library/unittest.mock.html#asynctest-support] [VERIFIED: local Python 3.14.3] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| parser-only pytest stack | `pytest-homeassistant-custom-component` | Adds HA runtime complexity and is explicitly out of scope for this phase. [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`] |

**Installation:**
```bash
py -m pip install pytest pytest-asyncio
```

**Version verification (executed):**
- `pytest 9.0.3`, uploaded `2026-04-07T17:16:18Z`. [VERIFIED: PyPI JSON API]
- `pytest-asyncio 1.3.0`, uploaded `2025-11-10T16:07:47Z`. [VERIFIED: PyPI JSON API]

## Architecture Patterns

### System Architecture Diagram

```text
Local HTML fixture files
        |
        v
pytest parameterized tests  ---> expected output contracts (JSON-like dict shape / explicit failure semantics)
        |
        +--> pure parser units: _extract_javascript_array(), _normalize_schedule()
        |
        +--> async parser API: get_schedule(), get_all_hdo_numbers()
                      |
                      v
            patched fetch_page() seam (no network)
                      |
                      v
            deterministic parser outputs/failures
```

### Recommended Project Structure
```text
tests/
├── fixtures/                    # local HTML inputs + expected snapshots (if used)
│   └── parser/
│       ├── standard_household_business.html
│       ├── malformed_js_array.html
│       ├── missing_var_name.html
│       └── mixed_code_types.html
├── test_parser_extract.py       # _extract_javascript_array behavior contracts
├── test_parser_normalize.py     # _normalize_schedule contracts
├── test_parser_get_schedule.py  # async API contracts with patched fetch_page
└── conftest.py                  # shared fixture loaders/helpers
```

### Pattern 1: Fixture-driven deterministic parser unit tests
**What:** Feed fixed HTML payloads into `_extract_javascript_array` and assert exact normalized list semantics (including expected empty-list failures). [VERIFIED: `custom_components/zse_hdo/parser.py`]  
**When to use:** For parser-format contract checks independent of network and wall-clock. [VERIFIED: `.planning/ROADMAP.md`]

**Example:**
```python
import pytest
from custom_components.zse_hdo.parser import ZSEHDOLiveParser

@pytest.mark.parametrize(
    "var_name, expected_count",
    [("household_rates", 2), ("business_rates", 1)],
)
def test_extract_javascript_array_happy_path(html_fixture, var_name, expected_count):
    parser = ZSEHDOLiveParser()
    data = parser._extract_javascript_array(html_fixture, var_name)
    assert isinstance(data, list)
    assert len(data) == expected_count
```
Source pattern: pytest fixtures + parametrization. [CITED: https://docs.pytest.org/en/stable/how-to/fixtures.html]

### Pattern 2: Async parser API tests with patched I/O seam
**What:** Patch `fetch_page` to return local fixture content, then assert `get_schedule()` shape and deterministic failure return values. [VERIFIED: `custom_components/zse_hdo/parser.py`]  
**When to use:** For `PARS-04` coverage of public parser entry points without live HTTP. [VERIFIED: `.planning/REQUIREMENTS.md`]

**Example:**
```python
import pytest
from unittest.mock import AsyncMock, patch
from custom_components.zse_hdo.parser import ZSEHDOLiveParser

@pytest.mark.asyncio
async def test_get_schedule_returns_none_for_unknown_hdo(html_fixture):
    parser = ZSEHDOLiveParser()
    with patch.object(parser, "fetch_page", AsyncMock(return_value=html_fixture)):
        schedule = await parser.get_schedule(999999)
    assert schedule is None
```
Source pattern: pytest-asyncio marker + AsyncMock patching. [CITED: https://pytest-asyncio.readthedocs.io/en/stable/, https://docs.python.org/3/library/unittest.mock.html#asynctest-support]

### Anti-Patterns to Avoid
- **Live-network parser tests:** Creates flakiness and violates D-03 deterministic fixture constraint. [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`]
- **HA harness in this phase:** Introduces unnecessary complexity and conflicts with D-02 scope. [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`]
- **Asserting only "not None":** Misses regression in output shape required by D-04. [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async test loop orchestration | Custom event-loop runner script | `pytest-asyncio` | Standard plugin already solves coroutine test execution and loop config safely. [CITED: https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html] |
| Fixture dependency graph management | Homemade test setup registry | pytest fixtures (`conftest.py`) | pytest fixture scopes and injection are standard and maintainable. [CITED: https://docs.pytest.org/en/stable/how-to/fixtures.html] |
| Async method stubbing helpers | Custom async fake classes | `unittest.mock.AsyncMock` | Stdlib async-aware mocks reduce boilerplate and signature drift risk. [CITED: https://docs.python.org/3/library/unittest.mock.html#asynctest-support] |

**Key insight:** Phase 3 risk is regression detection quality, not framework novelty; use battle-tested primitives and keep tests laser-focused on parser contracts. [VERIFIED: `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`]

## Common Pitfalls

### Pitfall 1: Non-deterministic tariff assertions
**What goes wrong:** `get_schedule()` assertions fail intermittently due to `current_tariff` depending on current time. [VERIFIED: `custom_components/zse_hdo/parser.py`]  
**Why it happens:** `get_schedule()` calls `_calculate_current_tariff()` using `dt_util.now()`. [VERIFIED: `custom_components/zse_hdo/parser.py`]  
**How to avoid:** In `get_schedule` tests, patch `_calculate_current_tariff()` to a stable value or assert only structural keys while unit-testing tariff logic separately. [VERIFIED: `custom_components/zse_hdo/parser.py`]  
**Warning signs:** CI passes/fails by time-of-day without fixture changes. [ASSUMED]

### Pitfall 2: Over-testing internals, under-testing API contract
**What goes wrong:** Tests pass while consumer-facing schedule shape regresses. [VERIFIED: `.planning/ROADMAP.md`]  
**Why it happens:** Coverage focuses only on helper methods, not `get_schedule()` payload contract. [VERIFIED: `custom_components/zse_hdo/parser.py`]  
**How to avoid:** Add explicit key-set/value-type assertions for `hdo_number`, `category`, `workday`, `weekend`, `current_tariff`, and failure paths (`None`, `[]`). [VERIFIED: `custom_components/zse_hdo/parser.py`]  
**Warning signs:** Refactor changes response keys but helper tests still green. [ASSUMED]

### Pitfall 3: Fixture drift from real source structure
**What goes wrong:** Fixture tests become too synthetic and miss real-world format shifts. [ASSUMED]  
**Why it happens:** Manually composed fixtures omit quirks of embedded JS arrays from `zsdis.sk`. [VERIFIED: `custom_components/zse_hdo/parser.py`, `CLAUDE.md`]  
**How to avoid:** Seed at least one fixture from captured real HTML and derive edge fixtures by minimal edits. [ASSUMED]  
**Warning signs:** Production parse failures despite broad local fixture suite. [ASSUMED]

## Code Examples

Verified patterns from official sources:

### Shared fixture loader (`conftest.py`)
```python
import pathlib
import pytest

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "parser"

@pytest.fixture
def html_fixture():
    return (FIXTURES / "standard_household_business.html").read_text(encoding="utf-8")
```
Source pattern: pytest fixtures via `@pytest.fixture`. [CITED: https://docs.pytest.org/en/stable/how-to/fixtures.html]

### Async test configuration
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```
Source pattern: pytest-asyncio configuration. [CITED: https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual smoke execution (`python parser.py`) | Automated fixture tests in pytest | Not yet in repo; planned in this phase | Enables repeatable pre-deploy regression checks for parser behavior. [VERIFIED: `.planning/codebase/TESTING.md`, `custom_components/zse_hdo/parser.py`] |

**Deprecated/outdated:**
- Relying only on ad-hoc parser smoke runs for correctness gating is insufficient for `PARS-04`. [VERIFIED: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Time-of-day flakiness will appear in CI if `_calculate_current_tariff` is not stabilized in tests. | Common Pitfalls | Medium — false negatives/unstable test gate. |
| A2 | Best practice is to seed fixtures from captured production HTML and minimally mutate for edge cases. | Common Pitfalls | Low — test realism may be reduced if skipped. |
| A3 | API-shape-only assertions (without value semantics) could miss meaningful regressions. | Common Pitfalls | Medium — reduced defect-detection power. |

## Open Questions (RESOLVED)

1. **How strict should output-shape contracts be (exact full dict vs key subsets)?**
   - Resolution: Use targeted key/value contract assertions for required parser output fields (`hdo_number`, `category`, `workday`, `weekend`, `current_tariff`, `source`) instead of full-object snapshots.
   - Rationale: This satisfies D-04 regression-gate intent while avoiding brittle failures from volatile values (for example `last_updated`). [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`, `custom_components/zse_hdo/parser.py`]

2. **Should Phase 3 include any coordinator/sensor-facing compatibility checks?**
   - Resolution: Keep tests parser-layer only, but include downstream-facing parser payload key checks in `get_schedule` tests.
   - Rationale: Honors D-02 parser-only scope and still protects parser-to-consumer contract shape required by `PARS-04`. [VERIFIED: `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md`, `.planning/REQUIREMENTS.md`]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python runtime | Running tests | ✓ | 3.14.3 | — |
| pip | Installing test deps | ✓ | 26.0.1 | — |
| pytest | Test execution | ✓ | 9.0.3 | install via `py -m pip install pytest` |
| pytest-asyncio | Async parser tests | ✓ | 1.3.0 | install/upgrade via `py -m pip install pytest-asyncio` |

**Missing dependencies with no fallback:**
- None. [VERIFIED: local shell checks]

**Missing dependencies with fallback:**
- None. [VERIFIED: local shell checks]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 + pytest-asyncio 1.3.0 [VERIFIED: local shell checks, PyPI JSON API] |
| Config file | none — add `pytest.ini` in Wave 0 [VERIFIED: `.planning/codebase/TESTING.md`] |
| Quick run command | `py -m pytest tests/test_parser_extract.py tests/test_parser_normalize.py -q -x` |
| Full suite command | `py -m pytest tests -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PARS-04 | Common parser inputs return expected normalized model shape | unit + async unit | `py -m pytest tests/test_parser_extract.py tests/test_parser_normalize.py tests/test_parser_get_schedule.py -q -x` | ❌ Wave 0 |
| PARS-04 | Problematic inputs fail deterministically (`[]`, `None`, or stable parse-failure behavior) | unit + async unit | `py -m pytest tests/test_parser_extract.py tests/test_parser_get_schedule.py -q -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `py -m pytest tests/test_parser_extract.py tests/test_parser_normalize.py -q -x`
- **Per wave merge:** `py -m pytest tests -q`
- **Phase gate:** Full parser fixture suite green before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/conftest.py` — shared fixture loader utilities.
- [ ] `tests/fixtures/parser/*.html` — deterministic source inputs for standard + problematic variants.
- [ ] `tests/test_parser_extract.py` — extraction contract tests.
- [ ] `tests/test_parser_normalize.py` — normalization contract tests.
- [ ] `tests/test_parser_get_schedule.py` — async API tests with patched `fetch_page`.
- [ ] `pytest.ini` — `asyncio_mode=auto`, `testpaths=tests`.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not applicable to offline parser fixture tests. [VERIFIED: phase scope] |
| V3 Session Management | no | Not applicable to parser-only phase. [VERIFIED: phase scope] |
| V4 Access Control | no | Not applicable to parser-only phase. [VERIFIED: phase scope] |
| V5 Input Validation | yes | Validate parser behavior on malformed HTML/JS fixture inputs and enforce deterministic failures. [VERIFIED: `custom_components/zse_hdo/parser.py`, `.planning/REQUIREMENTS.md`] |
| V6 Cryptography | no | No cryptographic primitives introduced in this phase. [VERIFIED: phase scope] |

### Known Threat Patterns for parser fixture stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed embedded JavaScript causing parse ambiguity | Tampering | Add malformed fixture cases and assert deterministic `[]`/error-path behavior. [VERIFIED: `custom_components/zse_hdo/parser.py`] |
| Silent contract drift in parser output keys | Tampering | Enforce explicit output-shape assertions in tests for downstream-required keys. [VERIFIED: `.planning/ROADMAP.md`, `custom_components/zse_hdo/parser.py`] |
| External source format change undetected until runtime | Repudiation/Availability | Include representative source-like fixture and run parser suite before releases. [VERIFIED: `.planning/ROADMAP.md`, `CLAUDE.md`] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/03-parser-verification-fixtures/03-CONTEXT.md` - locked decisions and scope boundaries.
- `.planning/REQUIREMENTS.md` - formal `PARS-04` requirement definition.
- `.planning/ROADMAP.md` - Phase 3 goal and success criteria.
- `.planning/codebase/TESTING.md` - current test-infra baseline (none configured).
- `custom_components/zse_hdo/parser.py` - parser contracts and deterministic failure semantics.
- [pytest docs](https://docs.pytest.org/en/stable/) - core test framework behavior.
- [pytest fixtures guide](https://docs.pytest.org/en/stable/how-to/fixtures.html) - fixture patterns and organization.
- [pytest-asyncio docs](https://pytest-asyncio.readthedocs.io/en/stable/) - asyncio test execution model.
- [pytest-asyncio configuration](https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html) - `asyncio_mode` and loop settings.
- [Python `unittest.mock` AsyncMock docs](https://docs.python.org/3/library/unittest.mock.html#asynctest-support) - async patching guidance.
- PyPI JSON APIs for `pytest` and `pytest-asyncio` - current versions and upload timestamps.

### Secondary (MEDIUM confidence)
- None.

### Tertiary (LOW confidence)
- None beyond explicitly tagged `[ASSUMED]` operational heuristics.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - official docs + live version verification.
- Architecture: HIGH - direct mapping from parser implementation and locked scope decisions.
- Pitfalls: MEDIUM - code-grounded plus a few operational assumptions explicitly marked.

**Research date:** 2026-04-29  
**Valid until:** 2026-05-29
