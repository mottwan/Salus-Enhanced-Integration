"""Salus Enhanced Integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEVICE_ID,
    CONF_EUID,
    CONF_GATEWAY_TYPE,
    DOMAIN,
    GATEWAY_TYPE_IT500,
    GATEWAY_TYPE_IT600,
    SCAN_INTERVAL,
    SUPPORTED_PLATFORMS,
)
from .gateway import create_gateway

if TYPE_CHECKING:
    from .coordinator import SalusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Salus Enhanced from a config entry."""
    gateway_type = entry.data[CONF_GATEWAY_TYPE]
    
    # Create appropriate gateway based on type
    if gateway_type == GATEWAY_TYPE_IT600:
        gateway = create_gateway(
            GATEWAY_TYPE_IT600,
            host=entry.data[CONF_HOST],
            euid=entry.data[CONF_EUID],
        )
        unique_name = entry.data[CONF_EUID]
    elif gateway_type == GATEWAY_TYPE_IT500:
        gateway = create_gateway(
            GATEWAY_TYPE_IT500,
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            device_id=entry.data[CONF_DEVICE_ID],
        )
        unique_name = entry.data[CONF_DEVICE_ID]
    else:
        _LOGGER.error("Unknown gateway type: %s", gateway_type)
        return False
    
    try:
        await gateway.connect()
        await gateway.poll_status()
    except Exception as err:
        _LOGGER.error("Failed to connect to gateway: %s", err)
        await gateway.close()
        raise ConfigEntryNotReady(f"Failed to connect to gateway: {err}") from err

    async def async_update_data():
        """Fetch data from gateway."""
        try:
            return await gateway.poll_status()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with gateway: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{unique_name}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "gateway": gateway,
        "coordinator": coordinator,
        "gateway_type": gateway_type,
    }

    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, SUPPORTED_PLATFORMS
    )

    if unload_ok:
        gateway = hass.data[DOMAIN][entry.entry_id]["gateway"]
        await gateway.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
