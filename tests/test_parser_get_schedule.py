"""Async API contract tests for parser get_schedule."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from unittest.mock import AsyncMock, patch

import pytest


def _load_parser_module():
    parser_path = Path(__file__).parents[1] / "custom_components" / "zse_hdo" / "parser.py"
    parser_dir = str(parser_path.parent)
    if parser_dir not in sys.path:
        sys.path.insert(0, parser_dir)
    spec = spec_from_file_location("zse_hdo_parser_under_test", parser_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_get_schedule_returns_expected_contract_keys(standard_parser_html):
    parser_module = _load_parser_module()
    parser = parser_module.ZSEHDOLiveParser()

    with patch.object(parser, "fetch_page", AsyncMock(return_value=standard_parser_html)):
        with patch.object(parser, "_calculate_current_tariff", return_value="low"):
            schedule = await parser.get_schedule(145)

    assert schedule is not None
    required_keys = {
        "hdo_number",
        "category",
        "workday",
        "weekend",
        "current_tariff",
        "source",
    }
    assert required_keys.issubset(set(schedule.keys()))
    assert schedule["hdo_number"] == 145
    assert schedule["category"] == "household"
    assert isinstance(schedule["workday"], list)
    assert isinstance(schedule["weekend"], list)
    assert schedule["current_tariff"] == "low"
    assert schedule["source"] == parser_module.ZSE_HDO_URL


@pytest.mark.asyncio
async def test_get_schedule_returns_none_for_unknown_hdo(standard_parser_html):
    parser = _load_parser_module().ZSEHDOLiveParser()

    with patch.object(parser, "fetch_page", AsyncMock(return_value=standard_parser_html)):
        schedule = await parser.get_schedule(999999)

    assert schedule is None


@pytest.mark.asyncio
async def test_get_schedule_stays_offline_with_patched_fetch(standard_parser_html):
    parser = _load_parser_module().ZSEHDOLiveParser()

    with patch.object(parser, "fetch_page", AsyncMock(return_value=standard_parser_html)) as mocked_fetch:
        with patch.object(parser, "_calculate_current_tariff", return_value="high"):
            await parser.get_schedule(220)

    mocked_fetch.assert_awaited_once()
