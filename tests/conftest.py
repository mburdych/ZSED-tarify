"""Shared fixtures for parser contract tests."""

from pathlib import Path

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "parser"


def load_parser_fixture(filename: str) -> str:
    """Load parser HTML fixture content as UTF-8 text."""
    return (FIXTURES_DIR / filename).read_text(encoding="utf-8")


@pytest.fixture
def parser_fixture_loader():
    """Provide a callable fixture loader for parser tests."""
    return load_parser_fixture


@pytest.fixture
def standard_parser_html(parser_fixture_loader):
    """Fixture with both household and business arrays."""
    return parser_fixture_loader("standard_household_business.html")


@pytest.fixture
def malformed_parser_html(parser_fixture_loader):
    """Fixture with malformed JavaScript array content."""
    return parser_fixture_loader("malformed_js_array.html")


@pytest.fixture
def missing_var_parser_html(parser_fixture_loader):
    """Fixture where a target JS variable is intentionally absent."""
    return parser_fixture_loader("missing_var_name.html")
