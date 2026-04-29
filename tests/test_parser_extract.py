"""Contract tests for parser JavaScript array extraction."""

import pytest

from custom_components.zse_hdo.parser import ZSEHDOLiveParser


@pytest.mark.parametrize(
    ("var_name", "expected_count"),
    [
        ("household_rates", 1),
        ("business_rates", 2),
    ],
)
def test_extract_javascript_array_parses_known_arrays(
    standard_parser_html, var_name, expected_count
):
    parser = ZSEHDOLiveParser()

    data = parser._extract_javascript_array(standard_parser_html, var_name)

    assert isinstance(data, list)
    assert len(data) == expected_count


@pytest.mark.parametrize(
    ("fixture_name", "var_name"),
    [
        ("missing_var_name.html", "household_rates"),
        ("malformed_js_array.html", "household_rates"),
    ],
)
def test_extract_javascript_array_returns_empty_on_invalid_input(
    parser_fixture_loader, fixture_name, var_name
):
    parser = ZSEHDOLiveParser()
    html = parser_fixture_loader(fixture_name)

    data = parser._extract_javascript_array(html, var_name)

    assert data == []
