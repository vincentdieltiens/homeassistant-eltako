"""The eltako integration."""
from __future__ import annotations


from .eltako_bus import EltakoBus

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE, Platform
from homeassistant.core import Config, HomeAssistant

from .dongle import EnOceanDongle
from .const import DATA_ELTAKO, DOMAIN
import asyncio


async def async_setup(hass: HomeAssistant, config) -> bool:

    hass.states.async_set("eltako.loaded", "False")

    # bus = EltakoBus()
    # hass.data[DOMAIN] = {}
    # hass.data[DOMAIN]["bus"] = bus

    print("Eltako Initialized!")

    return True


async def listen_bus(bus):
    """Listen the bus asynchronously"""
    print("VINCENT : Listen....")
    # bus.listen()
    print("VINCENT : done listen")


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up eltako from a config entry."""
    # TODO Optionally store an object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = ...

    # TODO Optionally validate config entry options before setting up platform
    print("Ole oleeeeeee")
    # hass.config_entries.async_setup_platforms(entry, (Platform.LIGHT,))

    # bus = hass.data[DOMAIN]["bus"]
    # asyncio.create_task(listen_bus(bus))

    # TODO Remove if the integration does not have an options flow
    # entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    eltako_data = hass.data.setdefault(DATA_ELTAKO, {})
    usb_dongle = EnOceanDongle(hass, config_entry.data[CONF_DEVICE])
    await usb_dongle.async_setup()
    eltako_data["dongle"] = usb_dongle

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload ENOcean config entry."""
    usb_dongle = hass.data[DATA_ELTAKO]["dongle"]
    usb_dongle.unload()
    hass.data.pop(DATA_ELTAKO)
    return True


# TODO Remove if the integration does not have an options flow
async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    # await hass.config_entries.async_reload(entry.entry_id)
