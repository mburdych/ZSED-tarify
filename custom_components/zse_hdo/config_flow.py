"""Config flow for ZSE HDO Live integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN, 
    CONF_HDO_NUMBER, 
    CONF_UPDATE_FREQUENCY,
    UPDATE_FREQUENCIES,
    DEFAULT_UPDATE_FREQUENCY
)
from .parser import ZSEHDOLiveParser

_LOGGER = logging.getLogger(__name__)


class ZSEHDOConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZSE HDO."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._hdo_numbers = None
        self._errors = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step - load HDO numbers from ZSE website."""
        self._errors = {}

        if user_input is not None:
            # Validácia HDO čísla - konvertuj na int
            hdo_number = int(user_input[CONF_HDO_NUMBER])
            update_frequency = user_input.get(CONF_UPDATE_FREQUENCY, DEFAULT_UPDATE_FREQUENCY)
            
            # Kontrola duplicity
            await self.async_set_unique_id(f"zse_hdo_{hdo_number}")
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=f"ZSE HDO {hdo_number}",
                data={
                    CONF_HDO_NUMBER: hdo_number,
                    CONF_UPDATE_FREQUENCY: update_frequency
                }
            )

        # Načítanie zoznamu HDO čísel z webu
        if self._hdo_numbers is None:
            try:
                session = aiohttp_client.async_get_clientsession(self.hass)
                parser = ZSEHDOLiveParser(session=session)
                
                _LOGGER.info("Fetching HDO numbers from ZSE website...")
                self._hdo_numbers = await parser.get_all_hdo_numbers()
                
                # Zoradi HDO čísla vzostupne
                self._hdo_numbers.sort()
                
                _LOGGER.info(f"Found {len(self._hdo_numbers)} HDO numbers (sorted)")
                
            except Exception as err:
                _LOGGER.error(f"Failed to fetch HDO numbers: {err}")
                self._errors["base"] = "cannot_connect"
                self._hdo_numbers = []

        # Zobrazenie formulára s frekvenciou
        data_schema = vol.Schema({
            vol.Required(CONF_HDO_NUMBER): vol.In({
                str(hdo): f"HDO {hdo}" 
                for hdo in self._hdo_numbers
            }) if self._hdo_numbers else cv.string,
            vol.Required(
                CONF_UPDATE_FREQUENCY, 
                default=DEFAULT_UPDATE_FREQUENCY
            ): vol.In({
                key: config["label"]
                for key, config in UPDATE_FREQUENCIES.items()
            })
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors,
            description_placeholders={
                "hdo_count": str(len(self._hdo_numbers)) if self._hdo_numbers else "0"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ZSEHDOOptionsFlowHandler(config_entry)


class ZSEHDOOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for ZSE HDO."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options - zmena frekvencie aktualizácie."""
        if user_input is not None:
            # Aktualizuj config entry s novou frekvenciou
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    **self.config_entry.data,
                    CONF_UPDATE_FREQUENCY: user_input[CONF_UPDATE_FREQUENCY]
                }
            )
            
            # Reload integráciu pre aplikovanie zmien
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            return self.async_create_entry(title="", data=user_input)

        # Aktuálna frekvencia
        current_frequency = self.config_entry.data.get(
            CONF_UPDATE_FREQUENCY, 
            DEFAULT_UPDATE_FREQUENCY
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_UPDATE_FREQUENCY,
                    default=current_frequency
                ): vol.In({
                    key: config["label"]
                    for key, config in UPDATE_FREQUENCIES.items()
                })
            })
        )
