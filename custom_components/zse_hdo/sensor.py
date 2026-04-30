"""Sensor platform for ZSE HDO Live integration.

Provides binary sensor for tariff status and sensors for next switch time
and today's schedule.

Author: Miroslav Burdych (@mburdych)
GitHub: https://github.com/mburdych/ZSED-tarify
Support: https://buymeacoffee.com/mburdych

License: MIT
"""

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .time_semantics import calculate_next_switch, get_periods_for_datetime, is_low_tariff

_LOGGER = logging.getLogger(__name__)


def _reliability_attrs(data: Dict[str, Any]) -> Dict[str, Any]:
    """Project coordinator reliability metadata into entity attributes."""
    return {
        "is_stale": data.get("is_stale", False),
        "stale_for_s": data.get("stale_for_s", 0),
        "consecutive_failures": data.get("consecutive_failures", 0),
        "last_success_at": data.get("last_success_at"),
        "last_error_at": data.get("last_error_at"),
        "next_retry_at": data.get("next_retry_at"),
        "diagnostic_error_source": data.get("diagnostic_error_source"),
        "diagnostic_error_code": data.get("diagnostic_error_code"),
        "diagnostic_error_at": data.get("diagnostic_error_at"),
    }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ZSE HDO sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    hdo_number = hass.data[DOMAIN][entry.entry_id]["hdo_number"]
    
    entities = [
        ZSEHDOTariffSensor(coordinator, entry, hdo_number),
        ZSEHDONextSwitchSensor(coordinator, entry, hdo_number),
        ZSEHDOTodayScheduleSensor(coordinator, entry, hdo_number),
        ZSEHDOLowRemainingSensor(coordinator, entry, hdo_number),
    ]
    
    async_add_entities(entities)


class ZSEHDOTariffSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor pre aktuálnu tarifu (ON = nízka, OFF = vysoká)."""

    def __init__(self, coordinator, entry: ConfigEntry, hdo_number: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._hdo_number = hdo_number
        self._attr_unique_id = f"zse_hdo_{hdo_number}_tariff"
        self._attr_name = f"ZSE HDO {hdo_number} Tarifa"
        self._attr_device_class = BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool:
        """Return true if low tariff is active (calculated dynamically from schedule)."""
        if not self.coordinator.data:
            return False

        return is_low_tariff(self.coordinator.data, now=dt_util.now())

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "hdo_number": self._hdo_number,
            "current_tariff": self.coordinator.data.get("current_tariff"),
            "tariff_name": "Nízka tarifa" if self.is_on else "Vysoká tarifa",
            "category": self.coordinator.data.get("category"),
            "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
            "last_updated": self.coordinator.data.get("last_updated"),
            "source": self.coordinator.data.get("source"),
            **_reliability_attrs(self.coordinator.data),
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:flash" if self.is_on else "mdi:flash-off"


class ZSEHDONextSwitchSensor(CoordinatorEntity, SensorEntity):
    """Sensor pre najbližšie prepnutie tarify."""

    def __init__(self, coordinator, entry: ConfigEntry, hdo_number: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._hdo_number = hdo_number
        self._attr_unique_id = f"zse_hdo_{hdo_number}_next_switch"
        self._attr_name = f"ZSE HDO {hdo_number} Ďalšie prepnutie"
        self._attr_icon = "mdi:clock-outline"

    def _get_next_switch(self) -> Optional[Dict[str, Any]]:
        """Calculate next tariff switch."""
        if not self.coordinator.data:
            return None

        return calculate_next_switch(self.coordinator.data, now=dt_util.now())

    @property
    def native_value(self) -> Optional[str]:
        """Return the next switch time."""
        next_switch = self._get_next_switch()
        if next_switch:
            return next_switch["datetime"].isoformat()
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        next_switch = self._get_next_switch()
        if not next_switch:
            return {
                "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
                **_reliability_attrs(self.coordinator.data),
            }

        return {
            "time": next_switch["time"],
            "to_tariff": next_switch["to_tariff"],
            "to_tariff_name": "Nízka tarifa" if next_switch["to_tariff"] == "low" else "Vysoká tarifa",
            "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
            **_reliability_attrs(self.coordinator.data),
        }


class ZSEHDOTodayScheduleSensor(CoordinatorEntity, SensorEntity):
    """Sensor s dnešným rozvrhom."""

    def __init__(self, coordinator, entry: ConfigEntry, hdo_number: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._hdo_number = hdo_number
        self._attr_unique_id = f"zse_hdo_{hdo_number}_today_schedule"
        self._attr_name = f"ZSE HDO {hdo_number} Dnešný rozvrh"
        self._attr_icon = "mdi:calendar-today"

    @property
    def native_value(self) -> str:
        """Return the number of low tariff periods today."""
        if not self.coordinator.data:
            return "0"
        
        now = dt_util.now()
        is_weekend = now.weekday() >= 5

        periods = get_periods_for_datetime(self.coordinator.data, now)
        return str(len(periods))

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return today's schedule."""
        if not self.coordinator.data:
            return {}

        now = dt_util.now()
        is_weekend = now.weekday() >= 5

        periods = get_periods_for_datetime(self.coordinator.data, now)

        return {
            "day_type": "Víkend" if is_weekend else "Pracovný deň",
            "periods": periods,
            "period_count": len(periods),
            "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
            "category": self.coordinator.data.get("category"),
            **_reliability_attrs(self.coordinator.data),
        }


class ZSEHDOLowRemainingSensor(CoordinatorEntity, SensorEntity):
    """Helper sensor with remaining minutes in active low-tariff window."""

    def __init__(self, coordinator, entry: ConfigEntry, hdo_number: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._hdo_number = hdo_number
        self._attr_unique_id = f"zse_hdo_{hdo_number}_low_remaining"
        self._attr_name = f"ZSE HDO {hdo_number} Zostavajuca nizka tarifa"
        self._attr_icon = "mdi:timer-sand"
        self._attr_native_unit_of_measurement = "min"

    def _active_low_period_end(self) -> Optional[Any]:
        """Return end datetime for current low-tariff period."""
        if not self.coordinator.data:
            return None

        now = dt_util.now()
        if not is_low_tariff(self.coordinator.data, now=now):
            return None

        current_time = now.time()
        periods = get_periods_for_datetime(self.coordinator.data, now)
        for period in periods:
            start_str = period.get("start")
            end_str = period.get("end")
            if not start_str or not end_str:
                continue
            try:
                start_hour, start_minute = map(int, start_str.split(":"))
                end_hour, end_minute = map(int, end_str.split(":"))
            except (TypeError, ValueError):
                continue

            start_time = now.replace(
                hour=start_hour, minute=start_minute, second=0, microsecond=0
            ).time()
            end_time = now.replace(
                hour=end_hour, minute=end_minute, second=0, microsecond=0
            ).time()
            in_period = (
                current_time >= start_time or current_time < end_time
                if end_time < start_time
                else start_time <= current_time < end_time
            )
            if not in_period:
                continue

            end_dt = now.replace(
                hour=end_hour,
                minute=end_minute,
                second=0,
                microsecond=0,
            )
            if end_time < start_time and current_time >= start_time:
                end_dt = end_dt.replace(day=end_dt.day) + timedelta(days=1)
            return end_dt

        return None

    @property
    def native_value(self) -> int:
        """Return remaining low-tariff minutes (0 if inactive)."""
        period_end = self._active_low_period_end()
        if not period_end:
            return 0
        remaining_seconds = int((period_end - dt_util.now()).total_seconds())
        return max(0, remaining_seconds // 60)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return helper context attributes."""
        if not self.coordinator.data:
            return {}

        period_end = self._active_low_period_end()
        return {
            "remaining_minutes": self.native_value,
            "period_end": period_end.isoformat() if period_end else None,
            "is_low_tariff_now": self.native_value > 0,
            "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
            "category": self.coordinator.data.get("category"),
            **_reliability_attrs(self.coordinator.data),
        }
