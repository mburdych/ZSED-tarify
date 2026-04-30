"""ZSE HDO Data Coordinator.

Manages data fetching and updates for ZSE HDO integration.

Author: Miroslav Burdych (@mburdych)
GitHub: https://github.com/mburdych/ZSED-tarify
Support: https://buymeacoffee.com/mburdych

License: MIT
"""
import logging
import json
import hashlib
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
    SCHEDULED_UPDATE_HOUR,
    RETRY_BACKOFF_MIN_SECONDS,
    RETRY_BACKOFF_MAX_SECONDS,
    RETRY_BACKOFF_MULTIPLIER,
)
from .parser import ZSEHDOLiveParser
from .parser import (
    ZSEHDOFetchError,
    ZSEHDOParseError,
    ZSEHDOTariffLogicError,
)

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
        self._last_known_data = None
        self._last_success_at = None
        self._last_error_at = None
        self._consecutive_failures = 0
        self._next_retry_at = None
        self._scheduled_update_unsub = None
        self._retry_update_unsub = None
        self._diagnostic_error_source = None
        self._diagnostic_error_code = None
        self._diagnostic_error_at = None
        self._diagnostic_error_severity = None
        self._diagnostic_error_guidance = None
        self._last_schedule_fingerprint = None
        self._last_schedule_change_at = None
        self._schedule_changed = False

        # Pre interval typy (5min, 1hour) použij klasický update_interval
        if self.frequency_type == "interval":
            update_interval = timedelta(seconds=frequency_config["seconds"])
            _LOGGER.info(
                f"Initializing coordinator for HDO {hdo_number} "
                f"with interval: {frequency_config['label']} "
                f"({frequency_config['seconds']}s)"
            )
        else:
            # Pre scheduled typy (1day, 1week, 1month) - polling vypnutý, len async_track_point_in_time
            update_interval = None
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
        if self._scheduled_update_unsub:
            self._scheduled_update_unsub()
        
        # Naplánuj nový timer
        self._scheduled_update_unsub = async_track_point_in_time(
            self.hass,
            _scheduled_update,
            next_update
        )

    def _clear_retry_update(self):
        """Cancel pending retry timer."""
        if self._retry_update_unsub:
            self._retry_update_unsub()
            self._retry_update_unsub = None

    def _schedule_retry_update(self, retry_at: datetime):
        """Plan a one-shot retry for scheduled refresh modes."""
        if self.frequency_type != "scheduled":
            return

        self._clear_retry_update()

        async def _retry_update(now):
            """Run one retry refresh attempt."""
            self._retry_update_unsub = None
            _LOGGER.info(f"HDO {self.hdo_number}: Running retry update")
            await self.async_request_refresh()

        self._retry_update_unsub = async_track_point_in_time(
            self.hass,
            _retry_update,
            retry_at,
        )

    def _compute_retry_delay(self) -> int:
        """Compute bounded exponential backoff delay in seconds."""
        if self._consecutive_failures <= 0:
            return RETRY_BACKOFF_MIN_SECONDS

        raw_delay = RETRY_BACKOFF_MIN_SECONDS * (
            RETRY_BACKOFF_MULTIPLIER ** (self._consecutive_failures - 1)
        )
        return max(
            RETRY_BACKOFF_MIN_SECONDS,
            min(raw_delay, RETRY_BACKOFF_MAX_SECONDS),
        )

    def _calculate_stale_for_seconds(self, now: datetime) -> int:
        """Compute stale age for the last successful refresh."""
        if self._last_success_at is None:
            return 0
        return max(0, int((now - self._last_success_at).total_seconds()))

    def _enrich_schedule(
        self,
        schedule: Dict,
        now: datetime,
        is_stale: bool,
    ) -> Dict:
        """Return schedule payload with coordinator-owned reliability metadata."""
        payload = dict(schedule)
        payload["is_stale"] = is_stale
        payload["stale_for_s"] = self._calculate_stale_for_seconds(now) if is_stale else 0
        payload["last_success_at"] = (
            self._last_success_at.isoformat() if self._last_success_at else None
        )
        payload["last_error_at"] = (
            self._last_error_at.isoformat() if self._last_error_at else None
        )
        payload["consecutive_failures"] = self._consecutive_failures
        payload["next_retry_at"] = (
            self._next_retry_at.isoformat() if self._next_retry_at else None
        )
        payload["diagnostic_error_source"] = self._diagnostic_error_source
        payload["diagnostic_error_code"] = self._diagnostic_error_code
        payload["diagnostic_error_at"] = (
            self._diagnostic_error_at.isoformat() if self._diagnostic_error_at else None
        )
        payload["diagnostic_error_severity"] = self._diagnostic_error_severity
        payload["diagnostic_error_guidance"] = self._diagnostic_error_guidance
        payload["schedule_changed"] = self._schedule_changed
        payload["schedule_change_at"] = (
            self._last_schedule_change_at.isoformat()
            if self._last_schedule_change_at
            else None
        )
        return payload

    def _schedule_fingerprint(self, schedule: Dict) -> str:
        """Create stable fingerprint for schedule-only payload."""
        normalized = {
            "workday": schedule.get("workday", []),
            "weekend": schedule.get("weekend", []),
        }
        raw = json.dumps(normalized, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _classify_error(self, err: Exception) -> tuple[str, str, str, str]:
        """Map runtime exception to explicit diagnostic source/code/severity/help."""
        if isinstance(err, ZSEHDOFetchError):
            return (
                "fetch",
                "FETCH_ERROR",
                "warning",
                "Skontrolujte internetove pripojenie a dostupnost webu ZSDIS.",
            )
        if isinstance(err, ZSEHDOParseError):
            return (
                "parse",
                "PARSE_ERROR",
                "error",
                "Skontrolujte, ci sa nezmenila struktura zdrojovej stranky ZSDIS.",
            )
        if isinstance(err, ZSEHDOTariffLogicError):
            return (
                "tariff_logic",
                "TARIFF_LOGIC_ERROR",
                "error",
                "Skontrolujte HDO kod a validitu casovych intervalov.",
            )
        return (
            "fetch",
            "UNKNOWN_ERROR",
            "error",
            "Pozrite log integracie pre detail chyby a skuste obnovit entitu.",
        )

    async def _async_update_data(self) -> Dict:
        """Fetch data from ZSE."""
        now = dt_util.now()

        if (
            self._next_retry_at is not None
            and self._last_known_data is not None
            and now < self._next_retry_at
        ):
            return self._enrich_schedule(self._last_known_data, now, is_stale=True)

        try:
            _LOGGER.debug(f"Fetching schedule for HDO {self.hdo_number}")

            schedule = await self.parser.get_schedule(self.hdo_number)

            if schedule is None:
                raise ValueError(f"HDO {self.hdo_number} not found on ZSE website")

            _LOGGER.debug(
                f"Successfully loaded schedule for HDO {self.hdo_number} "
                f"(rate: {schedule.get('rate_type', 'Unknown')})"
            )

            self._last_success_at = now
            self._last_error_at = None
            self._consecutive_failures = 0
            self._next_retry_at = None
            self._clear_retry_update()
            self._diagnostic_error_source = None
            self._diagnostic_error_code = None
            self._diagnostic_error_at = None
            self._diagnostic_error_severity = None
            self._diagnostic_error_guidance = None
            new_fingerprint = self._schedule_fingerprint(schedule)
            self._schedule_changed = (
                self._last_schedule_fingerprint is not None
                and self._last_schedule_fingerprint != new_fingerprint
            )
            if self._schedule_changed:
                self._last_schedule_change_at = now
                _LOGGER.info(
                    "HDO %s: schedule change detected (fingerprint updated)",
                    self.hdo_number,
                )
            self._last_schedule_fingerprint = new_fingerprint

            payload = self._enrich_schedule(schedule, now, is_stale=False)
            self._last_known_data = payload
            return payload

        except Exception as err:
            (
                diagnostic_source,
                diagnostic_code,
                diagnostic_severity,
                diagnostic_guidance,
            ) = self._classify_error(err)
            _LOGGER.error(
                "Error fetching HDO data for %s [%s/%s]: %s",
                self.hdo_number,
                diagnostic_source,
                diagnostic_code,
                err,
            )
            self._last_error_at = now
            self._consecutive_failures += 1
            self._diagnostic_error_source = diagnostic_source
            self._diagnostic_error_code = diagnostic_code
            self._diagnostic_error_at = now
            self._diagnostic_error_severity = diagnostic_severity
            self._diagnostic_error_guidance = diagnostic_guidance
            retry_delay = self._compute_retry_delay()
            self._next_retry_at = now + timedelta(seconds=retry_delay)
            self._schedule_retry_update(self._next_retry_at)

            if self._last_known_data is not None:
                _LOGGER.warning(
                    f"HDO {self.hdo_number}: using cached schedule due to fetch error"
                )
                payload = self._enrich_schedule(self._last_known_data, now, is_stale=True)
                self._last_known_data = payload
                return payload

            raise UpdateFailed(f"Error fetching HDO data: {err}", retry_after=retry_delay)
