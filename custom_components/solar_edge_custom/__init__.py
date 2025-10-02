"""SolarEdge Custom integration."""

from __future__ import annotations

import socket

from aiohttp import ClientError
from .vendor.aiosolaredge import SolarEdge

from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_SITE_ID, LOGGER
from .types import SolarEdgeConfigEntry, SolarEdgeData

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: SolarEdgeConfigEntry) -> bool:
    """Set up SolarEdge from a config entry."""
    session = async_get_clientsession(hass)
    api = SolarEdge(entry.data[CONF_API_KEY], session)

    site_id = entry.data[CONF_SITE_ID]

    LOGGER.debug("Validating SolarEdge API access for site %s", site_id)

    try:
        response = await api.get_details(site_id)
    except (TimeoutError, ClientError, socket.gaierror) as ex:
        LOGGER.exception(
            "Could not retrieve details from SolarEdge API for site %s", site_id
        )
        raise ConfigEntryNotReady from ex

    LOGGER.debug(
        "SolarEdge details response for site %s received: %s", site_id, response
    )

    if "details" not in response:
        LOGGER.error(
            "Missing 'details' key in SolarEdge response for site %s: %s",
            site_id,
            response,
        )
        raise ConfigEntryNotReady

    status = response["details"].get("status")
    if status is None:
        LOGGER.error(
            "Missing 'status' in SolarEdge details response for site %s: %s",
            site_id,
            response["details"],
        )
        raise ConfigEntryNotReady

    if status.lower() != "active":
        LOGGER.error(
            "SolarEdge site %s is not active (status: %s)", site_id, status
        )
        return False

    entry.runtime_data = SolarEdgeData(api_client=api)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SolarEdgeConfigEntry) -> bool:
    """Unload SolarEdge config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
