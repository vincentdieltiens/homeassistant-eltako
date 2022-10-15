"""The eltako integration."""
from __future__ import annotations
from .eltako_bus import EltakoBus

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import Config, HomeAssistant

from .const import DOMAIN
import asyncio


async def async_setup(hass: HomeAssistant, config) -> bool:

    hass.states.async_set("eltako.loaded", "False")

    bus = EltakoBus()
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["bus"] = bus

    print("Eltako Initialized!")

    return True


async def listen_bus(bus):
    """Listen the bus asynchronously"""
    print("VINCENT : Listen....")
    bus.listen()
    print("VINCENT : done listen")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up eltako from a config entry."""
    # TODO Optionally store an object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = ...

    # TODO Optionally validate config entry options before setting up platform
    print("Ole oleeeeeee")
    hass.config_entries.async_setup_platforms(entry, (Platform.SENSOR,))

    bus = hass.data[DOMAIN]["bus"]
    asyncio.create_task(listen_bus(bus))

    # TODO Remove if the integration does not have an options flow
    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    return True


# TODO Remove if the integration does not have an options flow
async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, (Platform.SENSOR,)
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
