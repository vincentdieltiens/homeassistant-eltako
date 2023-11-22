"""The eltako integration."""
from __future__ import annotations

from .services import async_setup_services

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_DEVICE, Platform
from homeassistant.core import Config, HomeAssistant

from .dongle import EnOceanDongle
from .const import DATA_ELTAKO, DOMAIN, CONF_DELAY
import asyncio


async def async_setup(hass: HomeAssistant, config) -> bool:
    if not hass.data.get(DOMAIN):
        async_setup_services(hass)

    print("Eltako Initialized!")

    # support for text-based configuration (legacy)
    if DOMAIN not in config:
        return True

    # there is an entry available for our domain
    if hass.config_entries.async_entries(DOMAIN):
        # We can only have one dongle. If there is already one in the config,
        # there is no need to import the yaml based config.

        # The dongle is configured via the UI. The entities are configured via yaml
        return True

    # no USB dongle (or PiHat) is configured, yet
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
        )
    )

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

    config_entry.async_on_unload(config_entry.add_update_listener(config_entry_update_listener))

    eltako_data = hass.data.setdefault(DATA_ELTAKO, {})
    delay = config_entry.options.get(CONF_DELAY, 500)
    usb_dongle = EnOceanDongle(hass, config_entry.data[CONF_DEVICE], delay)
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
    await hass.config_entries.async_reload(entry.entry_id)
