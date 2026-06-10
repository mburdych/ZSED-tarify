"""Tests for shared tariff time semantics."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types

import pytest


def _load_time_semantics_module():
    root = Path(__file__).parents[1]
    package_dir = root / "custom_components" / "zse_hdo"

    homeassistant_pkg = types.ModuleType("homeassistant")
    homeassistant_pkg.__path__ = []
    sys.modules["homeassistant"] = homeassistant_pkg

    ha_util = types.ModuleType("homeassistant.util")
    ha_util.__path__ = []
    sys.modules["homeassistant.util"] = ha_util

    ha_dt = types.ModuleType("homeassistant.util.dt")
    sys.modules["homeassistant.util.dt"] = ha_dt

    module_path = package_dir / "time_semantics.py"
    spec = spec_from_file_location("custom_components.zse_hdo.time_semantics", module_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _schedule():
    return {
        "workday": [
            {"start": "05:45", "end": "08:15", "tariff": "low"},
            {"start": "11:45", "end": "14:15", "tariff": "low"},
            {"start": "17:45", "end": "20:15", "tariff": "low"},
            {"start": "23:45", "end": "05:45", "tariff": "low"},
        ],
        "weekend": [
            {"start": "05:45", "end": "08:15", "tariff": "low"},
            {"start": "23:45", "end": "05:45", "tariff": "low"},
        ],
    }


def test_next_switch_after_all_starts_today_points_to_tonight():
    module = _load_time_semantics_module()
    now = datetime(2026, 6, 10, 21, 0, tzinfo=timezone.utc)
    result = module.calculate_next_switch(_schedule(), now=now)
    assert result is not None
    assert result["to_tariff"] == "low"
    assert result["datetime"] == datetime(2026, 6, 10, 23, 45, tzinfo=timezone.utc)


def test_get_next_future_switch_skips_past_candidate():
    module = _load_time_semantics_module()
    now = datetime(2026, 6, 10, 15, 0, tzinfo=timezone.utc)
    stale = datetime(2026, 6, 9, 23, 45, tzinfo=timezone.utc)

    original = module.calculate_next_switch

    def fake_calculate_next_switch(schedule, now=None):
        if now and now <= stale:
            return {
                "time": "23:45",
                "datetime": stale,
                "to_tariff": "low",
                "period": {"start": "23:45", "end": "05:45"},
            }
        return original(schedule, now=now)

    module.calculate_next_switch = fake_calculate_next_switch
    result = module.get_next_future_switch(_schedule(), now=now)
    assert result is not None
    assert result["datetime"] > now
    assert result["to_tariff"] == "low"
    assert result["datetime"] == datetime(2026, 6, 10, 17, 45, tzinfo=timezone.utc)


def test_next_switch_inside_midnight_crossing_period_ends_tomorrow_morning():
    module = _load_time_semantics_module()
    now = datetime(2026, 6, 10, 0, 30, tzinfo=timezone.utc)
    result = module.calculate_next_switch(_schedule(), now=now)
    assert result is not None
    assert result["to_tariff"] == "high"
    assert result["datetime"] == datetime(2026, 6, 10, 5, 45, tzinfo=timezone.utc)
