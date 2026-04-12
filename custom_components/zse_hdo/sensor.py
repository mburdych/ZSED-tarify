"""Sensor platform for ZSE HDO Live integration.

Provides binary sensor for tariff status and sensors for next switch time
and today's schedule.

Author: Miroslav Burdych (@mburdych)
GitHub: https://github.com/mburdych/ZSED-tarify
Support: https://buymeacoffee.com/mburdych

License: MIT
"""

import logging
from datetime import datetime, time, timedelta
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

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


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

    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)

    @property
    def is_on(self) -> bool:
        """Return true if low tariff is active (calculated dynamically from schedule)."""
        if not self.coordinator.data:
            return False

        now = datetime.now()
        current_time = now.time()
        is_weekend = now.weekday() >= 5

        periods = self.coordinator.data["weekend"] if is_weekend else self.coordinator.data["workday"]

        for period in periods:
            start = self._parse_time(period["start"])
            end = self._parse_time(period["end"])

            if end < start:  # midnight crossing
                if current_time >= start or current_time < end:
                    return True
            else:
                if start <= current_time < end:
                    return True

        return False

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

    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)

    def _get_next_switch(self) -> Optional[Dict[str, Any]]:
        """Calculate next tariff switch."""
        if not self.coordinator.data:
            return None

        now = datetime.now()
        current_time = now.time()
        is_weekend = now.weekday() >= 5

        periods = self.coordinator.data["weekend"] if is_weekend else self.coordinator.data["workday"]

        # Step 1: check if we're currently inside a low-tariff period (including midnight-crossing).
        # If so, the next switch is to high tariff at that period's end.
        for period in periods:
            start = self._parse_time(period["start"])
            end = self._parse_time(period["end"])

            in_period = False
            if end < start:  # midnight crossing
                if current_time >= start or current_time < end:
                    in_period = True
            else:
                if start <= current_time < end:
                    in_period = True

            if in_period:
                end_dt = datetime.combine(now.date(), end)
                # If we're in the before-midnight half of a crossing period, end is tomorrow
                if end < start and current_time >= start:
                    end_dt = datetime.combine(now.date() + timedelta(days=1), end)
                return {
                    "time": end.strftime("%H:%M"),
                    "datetime": end_dt,
                    "to_tariff": "high",
                    "period": period
                }

        # Step 2: not in any period — find the next period start later today.
        candidates = []
        for period in periods:
            start = self._parse_time(period["start"])
            if start > current_time:
                candidates.append((datetime.combine(now.date(), start), period))

        if candidates:
            candidates.sort(key=lambda x: x[0])
            next_dt, next_period = candidates[0]
            return {
                "time": self._parse_time(next_period["start"]).strftime("%H:%M"),
                "datetime": next_dt,
                "to_tariff": "low",
                "period": next_period
            }

        # Step 3: nothing left today — return tomorrow's first period start.
        sorted_periods = sorted(periods, key=lambda p: self._parse_time(p["start"]))
        if sorted_periods:
            first_period = sorted_periods[0]
            start = self._parse_time(first_period["start"])
            return {
                "time": start.strftime("%H:%M"),
                "datetime": datetime.combine(now.date() + timedelta(days=1), start),
                "to_tariff": "low",
                "period": first_period
            }

        return None

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
        next_switch = self._get_next_switch()
        if not next_switch:
            return {}
        
        return {
            "time": next_switch["time"],
            "to_tariff": next_switch["to_tariff"],
            "to_tariff_name": "Nízka tarifa" if next_switch["to_tariff"] == "low" else "Vysoká tarifa",
            "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
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
        
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        
        periods = self.coordinator.data["weekend"] if is_weekend else self.coordinator.data["workday"]
        return str(len(periods))

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return today's schedule."""
        if not self.coordinator.data:
            return {}
        
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        
        periods = self.coordinator.data["weekend"] if is_weekend else self.coordinator.data["workday"]
        
        return {
            "day_type": "Víkend" if is_weekend else "Pracovný deň",
            "periods": periods,
            "period_count": len(periods),
            "rate_type": self.coordinator.data.get("rate_type", "Unknown"),
            "category": self.coordinator.data.get("category"),
        }
