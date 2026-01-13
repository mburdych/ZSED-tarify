"""ZSE HDO Data Coordinator."""
import logging
from datetime import datetime, timedelta, time
from typing import Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, 
    UPDATE_FREQUENCIES, 
    DEFAULT_UPDATE_FREQUENCY, 
    CONF_UPDATE_FREQUENCY,
    SCHEDULED_UPDATE_HOUR
)
from .parser import ZSEHDOLiveParser

_LOGGER = logging.getLogger(__name__)


class ZSEHDOCoordinator(DataUpdateCoordinator):
    """Coordinator pre ZSE HDO dáta."""

    def __init__(
        self,
        hass: HomeAssistant,
        parser: ZSEHDOLiveParser,
        hdo_number: int,
        update_frequency: str = DEFAULT_UPDATE_FREQUENCY,
    ):
        """Initialize coordinator."""
        self.parser = parser
        self.hdo_number = hdo_number
        self.update_frequency = update_frequency
        
        # Získaj konfiguráciu frekvencie
        frequency_config = UPDATE_FREQUENCIES.get(
            update_frequency, 
            UPDATE_FREQUENCIES[DEFAULT_UPDATE_FREQUENCY]
        )
        
        self.frequency_type = frequency_config.get("type", "interval")
        
        # Pre interval typy (5min, 1hour) použij klasický update_interval
        if self.frequency_type == "interval":
            update_interval = timedelta(seconds=frequency_config["seconds"])
            _LOGGER.info(
                f"Initializing coordinator for HDO {hdo_number} "
                f"with interval: {frequency_config['label']} "
                f"({frequency_config['seconds']}s)"
            )
        else:
            # Pre scheduled typy (1day, 1week, 1month) - prvý update hneď, potom scheduled
            update_interval = timedelta(minutes=5)  # Fallback, ale použijeme custom scheduling
            _LOGGER.info(
                f"Initializing coordinator for HDO {hdo_number} "
                f"with scheduled updates: {frequency_config['label']}"
            )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_hdo_{hdo_number}",
            update_interval=update_interval,
        )
        
        # Pre scheduled typy nastavíme vlastný timer
        if self.frequency_type == "scheduled":
            self._schedule_next_update()

    def _calculate_next_update(self) -> datetime:
        """Vypočítaj ďalší scheduled update čas."""
        now = dt_util.now()
        
        if self.update_frequency == "1day":
            # Každý deň o 03:00
            next_update = now.replace(hour=SCHEDULED_UPDATE_HOUR, minute=0, second=0, microsecond=0)
            if next_update <= now:
                next_update += timedelta(days=1)
                
        elif self.update_frequency == "1week":
            # Každý pondelok o 03:00
            next_update = now.replace(hour=SCHEDULED_UPDATE_HOUR, minute=0, second=0, microsecond=0)
            days_until_monday = (7 - now.weekday()) % 7  # 0 = pondelok
            if days_until_monday == 0 and next_update <= now:
                days_until_monday = 7
            next_update += timedelta(days=days_until_monday)
            
        elif self.update_frequency == "1month":
            # 1. deň mesiaca o 03:00
            next_update = now.replace(day=1, hour=SCHEDULED_UPDATE_HOUR, minute=0, second=0, microsecond=0)
            if next_update <= now:
                # Ďalší mesiac
                if now.month == 12:
                    next_update = next_update.replace(year=now.year + 1, month=1)
                else:
                    next_update = next_update.replace(month=now.month + 1)
        else:
            # Fallback - zajtra o 03:00
            next_update = now.replace(hour=SCHEDULED_UPDATE_HOUR, minute=0, second=0, microsecond=0)
            next_update += timedelta(days=1)
        
        return next_update

    def _schedule_next_update(self):
        """Naplánuj ďalší scheduled update."""
        if self.frequency_type != "scheduled":
            return
            
        next_update = self._calculate_next_update()
        
        _LOGGER.info(
            f"HDO {self.hdo_number}: Next scheduled update at {next_update.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        async def _scheduled_update(now):
            """Vykonaj scheduled update."""
            _LOGGER.info(f"HDO {self.hdo_number}: Running scheduled update")
            await self.async_request_refresh()
            # Naplánuj ďalší update
            self._schedule_next_update()
        
        # Zruš starý timer ak existuje
        if hasattr(self, "_scheduled_update_unsub") and self._scheduled_update_unsub:
            self._scheduled_update_unsub()
        
        # Naplánuj nový timer
        self._scheduled_update_unsub = async_track_point_in_time(
            self.hass,
            _scheduled_update,
            next_update
        )

    async def _async_update_data(self) -> Dict:
        """Fetch data from ZSE."""
        try:
            _LOGGER.debug(f"Fetching schedule for HDO {self.hdo_number}")
            
            schedule = await self.parser.get_schedule(self.hdo_number)
            
            if schedule is None:
                raise UpdateFailed(
                    f"HDO {self.hdo_number} not found on ZSE website"
                )
            
            _LOGGER.debug(
                f"Successfully loaded schedule for HDO {self.hdo_number} "
                f"(rate: {schedule.get('rate_type', 'Unknown')})"
            )
            
            return schedule
            
        except Exception as err:
            _LOGGER.error(
                f"Error fetching HDO data for {self.hdo_number}: {err}"
            )
            raise UpdateFailed(f"Error fetching HDO data: {err}")
