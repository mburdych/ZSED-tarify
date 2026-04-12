# Testing Patterns

**Analysis Date:** 2026-04-12

## Test Framework

**Runner:** None — no test framework is configured or installed.

**Assertion Library:** None

**Run Commands:** Not applicable

## Test File Organization

**No test files exist in this repository.**

A scan of all `.py` files returns only six production modules:
- `custom_components/zse_hdo/__init__.py`
- `custom_components/zse_hdo/config_flow.py`
- `custom_components/zse_hdo/const.py`
- `custom_components/zse_hdo/coordinator.py`
- `custom_components/zse_hdo/parser.py`
- `custom_components/zse_hdo/sensor.py`

There are no `tests/` or `test/` directories, no `conftest.py`, no `pytest.ini`, no `setup.cfg`, and no `pyproject.toml` anywhere in the repository.

## Test Structure

Not applicable — no tests exist.

## Mocking

Not applicable — no tests exist.

## Fixtures and Factories

Not applicable — no tests exist.

## Coverage

**Requirements:** None enforced — no coverage configuration present.

## Test Types

**Unit Tests:** Not present
**Integration Tests:** Not present
**E2E Tests:** Not present

## Developer Example Script

`custom_components/zse_hdo/parser.py` contains a `main()` function at the module bottom (lines 407–446) that serves as a manual smoke test / usage example. It is guarded with `if __name__ == "__main__":` and requires a live network connection to `zsdis.sk`. This is not an automated test.

```python
async def main():
    """Príklad použitia parsera."""
    async with ZSEHDOLiveParser() as parser:
        all_hdo = await parser.get_all_hdo_numbers()
        schedule = await parser.get_schedule(145)
        is_low = await parser.is_low_tariff_now(145)
```

## Testability Assessment

The codebase has reasonable testability structure but requires work to actually test:

**Testable as-is:**
- `ZSEHDOLiveParser._parse_time` — pure function, no dependencies
- `ZSEHDOLiveParser._normalize_schedule` — pure function operating on dicts
- `ZSEHDOLiveParser._extract_javascript_array` — pure function on HTML string
- `ZSEHDOCoordinator._calculate_next_update` — time calculation logic

**Requires mocking to test:**
- `ZSEHDOLiveParser.fetch_page` — requires `aiohttp.ClientSession` mock
- `ZSEHDOLiveParser.get_schedule` — depends on `fetch_page`
- `ZSEHDOCoordinator._async_update_data` — depends on `parser.get_schedule`
- All sensor `@property` methods — require a coordinator with data fixture

**HA-specific testing:**
- Config flow (`ZSEHDOConfigFlow`) requires `homeassistant.test_util` harness
- Coordinator requires `HomeAssistant` instance from `pytest-homeassistant-custom-component`

## Recommended Testing Setup

To add tests consistent with Home Assistant custom integration standards:

1. Add `pytest-homeassistant-custom-component` to dev dependencies
2. Create `tests/` directory at project root
3. Create `tests/conftest.py` with HA fixtures
4. Test pure parsing logic with plain `pytest` + `pytest-asyncio`
5. Mock HTTP with `aioresponses` or `unittest.mock.AsyncMock`

File placement when tests are added:
- `tests/test_parser.py` — unit tests for `ZSEHDOLiveParser`
- `tests/test_coordinator.py` — coordinator fetch and scheduling
- `tests/test_sensor.py` — sensor property outputs
- `tests/test_config_flow.py` — config and options flow steps
- `tests/conftest.py` — shared fixtures

---

*Testing analysis: 2026-04-12*
