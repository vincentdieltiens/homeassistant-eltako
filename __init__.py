"""The eltako integration."""
from __future__ import annotations

from .services import async_setup_services

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_DEVICE, Platform
from homeassistant.core import Config, HomeAssistant

from .dongle import EnOceanDongle
from .const import DATA_ELTAKO, DOMAIN, CONF_DELAY, LOGGER, PLATFORMS
import asyncio


async def async_setup(hass: HomeAssistant, config) -> bool:
    #Async setup is called when HomeAssistant loads the integration

    # Sets the services defined by this integration (see services.py é services.yaml)
    if not hass.data.get(DOMAIN):
        async_setup_services(hass)

    LOGGER.debug("Eltako Initialized!" + str(config))

    # support for text-based configuration (legacy)
    if DOMAIN not in config:
        return True

    # there is an entry available for our domain
    if hass.config_entries.async_entries(DOMAIN):
        # We can only have one dongle. If there is already one in the config,
        # there is no need to import the yaml based config.

        # The dongle is configured via the UI. The entities are configured via yaml
        return True

    # No USB dongle (or PiHat) is configured, yet
    # Initialize the flow to add the integration
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up eltako from a config entry."""
    # This is called when at the start of the integration
    
    # TODO Optionally validate config entry options before setting up platform
    # hass.config_entries.async_setup_platforms(entry, (Platform.LIGHT,))
    #await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Needed by HomeAssistant when there is a ConfigFlow
    # With this line, config_entry_update_listener will be called when an 
    # option is updated from UI
    config_entry.async_on_unload(config_entry.add_update_listener(config_entry_update_listener))

    # Gets the delay defined in the integration options/configuration (via HA UI)
    # If the option is not defined, 500 is set as default value
    delay = config_entry.options.get(CONF_DELAY, 500)

    # Initialize the dongle
    usb_dongle = EnOceanDongle(hass, config_entry.data[CONF_DEVICE], delay)
    await usb_dongle.async_setup()

    # Sets the dongle in hass data object (under DATA_ETLAKO -> "dongle")
    eltako_data = hass.data.setdefault(DATA_ELTAKO, {})
    eltako_data["dongle"] = usb_dongle

    LOGGER.debug("VINCENT : dongle initialized. Saving config_entry_id")
    eltako_data["config_entry_id"] = config_entry.entry_id

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload ENOcean config entry."""
    # Called when the integration is removed from home assistant
    # We unload the dongle and remove all the data from hass data object

    usb_dongle = hass.data[DATA_ELTAKO]["dongle"]
    usb_dongle.unload()
    hass.data.pop(DATA_ELTAKO)
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    # Needed by HA when having a ConfigFlow and called when any option has
    # beed updated by the user using the configure button of the HA integration UI
    await hass.config_entries.async_reload(entry.entry_id)
