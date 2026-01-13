"""ZSE HDO Live Integration for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .parser import ZSEHDOLiveParser
from .coordinator import ZSEHDOCoordinator
from .const import (
    DOMAIN, 
    CONF_HDO_NUMBER, 
    CONF_UPDATE_FREQUENCY,
    DEFAULT_UPDATE_FREQUENCY
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ZSE HDO from a config entry."""
    hdo_number = entry.data[CONF_HDO_NUMBER]
    update_frequency = entry.data.get(CONF_UPDATE_FREQUENCY, DEFAULT_UPDATE_FREQUENCY)
    
    _LOGGER.info(
        f"Setting up ZSE HDO integration for HDO {hdo_number} "
        f"(frequency: {update_frequency})"
    )
    
    # Vytvorenie parsera
    session = async_get_clientsession(hass)
    parser = ZSEHDOLiveParser(session=session)
    
    # Vytvorenie coordinatora
    coordinator = ZSEHDOCoordinator(
        hass=hass,
        parser=parser,
        hdo_number=hdo_number,
        update_frequency=update_frequency
    )
    
    # Prvotné načítanie dát
    await coordinator.async_config_entry_first_refresh()
    
    # Uloženie do hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "parser": parser,
        "hdo_number": hdo_number,
    }
    
    # Setup platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
