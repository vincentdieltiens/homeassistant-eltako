""" Represent a binary sensor """


from ctypes import Union
import math
from typing import Any
import voluptuous as vol
from enocean.utils import combine_hex

from homeassistant.components.binary_sensor import (
    DEVICE_CLASSES_SCHEMA,
    PLATFORM_SCHEMA,
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from homeassistant.const import CONF_DEVICE_ID, CONF_DEVICE_CLASS, CONF_ID, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .device import EltakoEntity
from .const import DOMAIN, LOGGER, CONF_SENDER_ID, DATA_ELTAKO, CONF_ACTION
from .utils import hex_list_to_str

EVENT_BUTTON_PRESSED = "button_pressed"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_DEVICE_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Optional(CONF_ACTION): vol.Coerce(int)
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Binary Sensor platform for EnOcean."""
    print("VINCENT : SETUP binary sensors")

    device_id = config[CONF_DEVICE_ID]
    device_name: str = config[CONF_NAME]
    device_class: BinarySensorDeviceClass | None = config.get(CONF_DEVICE_CLASS)

    add_entities([EltakoBinarySensor(device_id, device_name, device_class)])


class EltakoBinarySensor(EltakoEntity, BinarySensorEntity):
    def __init__(
            self,
            device_id: list[int],
            device_name: str,
            device_class: BinarySensorDeviceClass | None,
        ) -> None:
            """Initialize the EnOcean binary sensor."""
            super().__init__(device_id, device_name)
            self._attr_device_class = device_class
            self.which = -1
            self.onoff = -1
            self._attr_unique_id = f"{combine_hex(device_id)}-{device_class}"
            self._attr_name = device_name

    def value_changed(self, packet):
        """Fire an event with the data that have changed.

        This method is called when there is an incoming packet associated
        with this platform.
        """
        LOGGER.debug("VINCENT : PUSHED BUTTON!!")

        pushed = None

        if packet.data[6] == 0x30:
            pushed = 1
        elif packet.data[6] == 0x20:
            pushed = 0

        action = packet.data[1]
        if action == 0x70:
            self.which = 0
            self.onoff = 0
        elif action == 0x50:
            self.which = 0
            self.onoff = 1
        elif action == 0x30:
            self.which = 1
            self.onoff = 0
        elif action == 0x10:
            self.which = 1
            self.onoff = 1
        elif action == 0x37:
            self.which = 10
            self.onoff = 0
        elif action == 0x15:
            self.which = 10
            self.onoff = 1

        event = {
            "id": self.device_id,
            "pushed": pushed,
            "which": self.which,
            "onoff": self.onoff,
            "action": action
        }

        LOGGER.debug("VINCENT : FIRE EVENT_BUTTON_PRESSED. id = " + str(event))

        self.hass.bus.fire(
            EVENT_BUTTON_PRESSED,
            event,
        )