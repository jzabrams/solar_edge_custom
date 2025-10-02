"""Typing for the SolarEdge Custom integration."""

from __future__ import annotations

from typing import TypedDict

from .vendor.aiosolaredge import SolarEdge

from homeassistant.config_entries import ConfigEntry

type SolarEdgeConfigEntry = ConfigEntry[SolarEdgeData]


class SolarEdgeData(TypedDict):
    """Runtime data for the SolarEdge Custom integration."""

    api_client: SolarEdge
