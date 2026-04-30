"""Contract tests for parser JavaScript array extraction."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

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


@pytest.mark.parametrize(
    ("var_name", "expected_count"),
    [
        ("household_rates", 1),
        ("business_rates", 1),
    ],
)
def test_extract_javascript_array_parses_known_arrays(
    standard_parser_html, var_name, expected_count
):
    parser = _load_parser_module().ZSEHDOLiveParser()

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
def test_extract_javascript_array_raises_on_invalid_input(
    parser_fixture_loader, fixture_name, var_name
):
    module = _load_parser_module()
    parser = module.ZSEHDOLiveParser()
    html = parser_fixture_loader(fixture_name)

    with pytest.raises(module.ZSEHDOParseError):
        parser._extract_javascript_array(html, var_name)
