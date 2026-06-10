"""
ZSE HDO Time Semantics
======================

Shared helper functions pre tariff/day-type/midnight semantiku.

Author: Miroslav Burdych (@mburdych)
GitHub: https://github.com/mburdych/ZSED-tarify
Support: https://buymeacoffee.com/mburdych

License: MIT
"""

from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional

try:
    from homeassistant.util import dt as dt_util
except ImportError:  # pragma: no cover - fallback pre standalone parser smoke test
    class _FallbackDTUtil:
        @staticmethod
        def now() -> datetime:
            return datetime.now()

    dt_util = _FallbackDTUtil()


def parse_time(time_str: str) -> Optional[time]:
    """Parse HH:MM time string to time object."""
    try:
        hour, minute = map(int, time_str.split(":"))
        return time(hour=hour, minute=minute)
    except (AttributeError, TypeError, ValueError):
        return None


def get_periods_for_datetime(
    schedule: Dict[str, List[Dict[str, Any]]], candidate_dt: datetime
) -> List[Dict[str, Any]]:
    """Select workday/weekend periods for provided datetime."""
    is_weekend = candidate_dt.weekday() >= 5
    return schedule.get("weekend", []) if is_weekend else schedule.get("workday", [])


def is_time_in_period(current_time: time, start: time, end: time) -> bool:
    """Canonical inclusive/exclusive period predicate with midnight crossover."""
    if end < start:
        return current_time >= start or current_time < end
    return start <= current_time < end


def calculate_current_tariff(
    schedule: Dict[str, List[Dict[str, Any]]], now: Optional[datetime] = None
) -> str:
    """Return current tariff ('low'/'high') for provided schedule and datetime."""
    now_dt = now or dt_util.now()
    current_time = now_dt.time()
    periods = get_periods_for_datetime(schedule, now_dt)

    for period in periods:
        start = parse_time(period.get("start"))
        end = parse_time(period.get("end"))
        if not start or not end:
            continue
        if is_time_in_period(current_time, start, end):
            return "low"

    return "high"


def is_low_tariff(
    schedule: Dict[str, List[Dict[str, Any]]], now: Optional[datetime] = None
) -> bool:
    """Return True when current tariff is low."""
    return calculate_current_tariff(schedule, now=now) == "low"


def calculate_next_switch(
    schedule: Dict[str, List[Dict[str, Any]]], now: Optional[datetime] = None
) -> Optional[Dict[str, Any]]:
    """Calculate next tariff switch payload compatible with current sensor contract."""
    now_dt = now or dt_util.now()
    current_time = now_dt.time()
    periods = get_periods_for_datetime(schedule, now_dt)

    # Step 1: currently inside low period => next switch to high at period end.
    for period in periods:
        start = parse_time(period.get("start"))
        end = parse_time(period.get("end"))
        if not start or not end:
            continue
        if is_time_in_period(current_time, start, end):
            end_dt = datetime.combine(now_dt.date(), end, tzinfo=now_dt.tzinfo)
            if end < start and current_time >= start:
                end_dt = datetime.combine(now_dt.date() + timedelta(days=1), end, tzinfo=now_dt.tzinfo)
            return {
                "time": end.strftime("%H:%M"),
                "datetime": end_dt,
                "to_tariff": "high",
                "period": period,
            }

    # Step 2: next start later today.
    candidates = []
    for period in periods:
        start = parse_time(period.get("start"))
        if not start:
            continue
        if start > current_time:
            candidates.append((datetime.combine(now_dt.date(), start, tzinfo=now_dt.tzinfo), period))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        next_dt, next_period = candidates[0]
        start = parse_time(next_period.get("start"))
        if not start:
            return None
        return {
            "time": start.strftime("%H:%M"),
            "datetime": next_dt,
            "to_tariff": "low",
            "period": next_period,
        }

    # Step 3: nothing left today => tomorrow's first period.
    tomorrow_dt = now_dt + timedelta(days=1)
    tomorrow_periods = get_periods_for_datetime(schedule, tomorrow_dt)
    sorted_periods = sorted(
        tomorrow_periods,
        key=lambda period: parse_time(period.get("start")) or time.max,
    )

    for period in sorted_periods:
        start = parse_time(period.get("start"))
        if not start:
            continue
        return {
            "time": start.strftime("%H:%M"),
            "datetime": datetime.combine(tomorrow_dt.date(), start, tzinfo=now_dt.tzinfo),
            "to_tariff": "low",
            "period": period,
        }

    return None


def get_next_future_switch(
    schedule: Dict[str, List[Dict[str, Any]]], now: Optional[datetime] = None
) -> Optional[Dict[str, Any]]:
    """Return the next tariff switch strictly in the future relative to `now`."""
    now_dt = now or dt_util.now()
    probe = now_dt
    for _ in range(20):
        candidate = calculate_next_switch(schedule, now=probe)
        if not candidate:
            return None
        if candidate["datetime"] > now_dt:
            return candidate
        probe = candidate["datetime"] + timedelta(seconds=1)
    return None
