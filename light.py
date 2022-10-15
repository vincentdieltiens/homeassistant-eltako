""" Represent a light """

from ctypes import Union
from typing import Any
import voluptuous as vol
import logging
import time
from .eltako_bus import Packet

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import PLATFORM_SCHEMA, LightEntity
from homeassistant.const import CONF_DEVICE_ID, CONF_DEVICES, CONF_NAME
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
    }
)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    # {vol.Required(CONF_DEVICES, default={}): {cv.string: DEVICE_SCHEMA}}
    {vol.Required(CONF_NAME): cv.string, vol.Required(CONF_DEVICE_ID): cv.string}
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info,
) -> None:
    """Set up Eltako FS14R Light"""

    print("VINCENT : SETUP lights")
    _LOGGER.debug("VINCENT : setup lights")

    bus = hass.data[DOMAIN]["bus"]

    # bus = EltakoBus()

    # connect to lights
    # print("VINCENT : ", str(config.get(CONF_DEVICES, {})))
    lights = []

    name = config.get(CONF_NAME)
    sender_id_str = config[CONF_DEVICE_ID].split("-")
    sender_id = list(map(lambda v: int("0x" + v, 16), sender_id_str))
    lights.append(FSR14Entity(bus, config[CONF_DEVICE_ID], name, sender_id))
    print("VINCENT : add light %s - %s" % (name, config[CONF_DEVICE_ID]))

    # for device_id, device_config in config.get(CONF_DEVICES, {}).items():
    #     print("Eltako Light of ID : %s" % (device_id))
    #     name = device_config[CONF_NAME]
    #     sender_id_str = device_config[CONF_DEVICE_ID].split("-")
    #     sender_id = list(map(lambda v: int("0x" + v, 16), sender_id_str))

    #     print("LIGHT : %s" % (str(sender_id)))

    #     lights.append(FSR14Entity(bus, device_id, name, sender_id))

    # add entities
    add_entities(lights)


class LightPacket(Packet):
    """Represents a light packet for a simple light"""

    def __init__(self, sender):
        super().__init__(sender=sender, r_1=3)


class FSR14Entity(LightEntity):
    """Represents an Eltako FSR14 Light"""

    _attr_has_entity_name = True
    _attr_name = None
    _device_id = None
    _sender_id = None
    _bus = None

    def __init__(self, bus, device_id, name, sender_id):
        """Description"""
        self._is_on = None
        self._bus = bus
        self._attr_name = name
        self._device_id = device_id
        self._sender_id = sender_id

    @property
    def name(self):
        """Name of the entity."""
        return self._attr_name

    @property
    def is_on(self):
        return self._is_on

    @property
    def assumed_state(self) -> bool:
        return self._is_on is None

    def turn_on(self, **kwargs: Any) -> None:
        packet = LightPacket(sender=self._sender_id)
        self._bus.send(packet)
        self._is_on = True
        # return super().turn_on(**kwargs)

    def turn_off(self, **kwargs: Any) -> None:
        packet = LightPacket(sender=self._sender_id)
        self._bus.send(packet)
        self._is_on = False
        # return super().turn_off(**kwargs)
