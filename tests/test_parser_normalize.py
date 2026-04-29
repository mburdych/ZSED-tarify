"""Contract tests for parser schedule normalization."""

from custom_components.zse_hdo.parser import ZSEHDOLiveParser


def test_normalize_schedule_filters_nt_and_maps_day_buckets():
    parser = ZSEHDOLiveParser()

    intervals = [
        {
            "t_type": "nt",
            "t_from": "00:30",
            "t_to": "02:30",
            "weekday": True,
            "weekend": True,
            "meaning": "nocny pas",
            "for_rate": "D3",
        },
        {
            "t_type": "vt",
            "t_from": "02:30",
            "t_to": "04:30",
            "weekday": True,
            "weekend": True,
            "meaning": "vysoka",
            "for_rate": "D3",
        },
        {
            "t_type": "nt",
            "t_from": "13:00",
            "t_to": "14:00",
            "weekday": True,
            "weekend": False,
            "meaning": "obed",
            "for_rate": "D3",
        },
    ]

    schedule = parser._normalize_schedule(intervals)

    assert set(schedule.keys()) == {"workday", "weekend"}
    assert len(schedule["workday"]) == 2
    assert len(schedule["weekend"]) == 2
    assert all(period["tariff"] == "low" for period in schedule["workday"])
    assert all(period["start"] != "02:30" for period in schedule["workday"])
