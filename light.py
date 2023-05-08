""" Represent a light """

from ctypes import Union
import math
from typing import Any
import voluptuous as vol
from enocean.utils import combine_hex

import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_MODEL, CONF_NAME
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from enocean.protocol.constants import PACKET, RORG

from .device import EltakoEntity
from .const import DOMAIN, LOGGER, CONF_SENDER_ID

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_DEVICE_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Required(CONF_SENDER_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Optional(CONF_MODEL, default="F4SR14"): vol.In(["F4SR14", "FUD14"]),
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info,
) -> None:
    """Set up Eltako FS14R Light"""
    print("VINCENT : SETUP lights")

    device_id = config.get(CONF_DEVICE_ID)
    device_name = config.get(CONF_NAME)
    sender_id = config.get(CONF_SENDER_ID)
    model = config.get(CONF_MODEL)

    if model == "F4SR14":
        light = F4SR14Entity(device_id, device_name, sender_id)
    elif model == "FUD14":
        light = FUD14Entity(device_id, device_name, sender_id)

    add_entities([light])


class EltakoLightEntity(EltakoEntity, LightEntity):
    """Represents a generic Eltako light (F4SR14, FUD14)"""

    _is_on = None
    _sender_id = None
    _color_mode = None
    _supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, device_id, device_name, sender_id) -> None:
        super().__init__(device_id, device_name)
        self._is_on = None
        self._sender_id = sender_id

    @property
    def is_on(self):
        return self._is_on

    @property
    def assumed_state(self) -> bool:
        return self._is_on is None

    @property
    def color_mode(self):  # -> Union[ColorMode, str, None]:
        return self._color_mode

    @property
    def supported_color_modes(self):  # -> Union[set[ColorMode], set[str], None]:
        return self._supported_color_modes

    @property
    def unique_id(self):
        _id = self.device_id.copy()
        _id.extend(self._sender_id)
        return combine_hex(_id)


class F4SR14Entity(EltakoLightEntity):
    """Represents an Eltako F4SR14 Light"""

    def __init__(self, device_id, device_name, sender_id):
        """Description"""
        super().__init__(device_id, device_name, sender_id)
        self._color_mode = ColorMode.ONOFF
        self.model = "F4SR14"

    def turn_on(self, **kwargs: Any) -> None:
        # 0 0 0 0 1 0 0 1
        # 0 1 2 3 4 5 6 7
        data = [RORG.BS4, 0x01, 0x00, 0x00, 0x09]  #
        data.extend(self._sender_id)
        data.extend([0x00])  # status

        optional = [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00]
        # optional = [0x00]
        # optional.append(self.device_id)
        # optional.append([0x00, 0x00])
        self.send_command(data, optional, PACKET.RADIO)
        # don't set _is_on to true, wait for callback
        # self._is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        command = [RORG.BS4, 0x01, 0x00, 0x00, 0x08]
        command.extend(self._sender_id)
        command.extend([0x00])  # status

        optional = [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x34, 0x00]
        self.send_command(command, optional, PACKET.RADIO)

        # don't set ._is_on to false, wait for callback
        # self._is_on = False

    def value_changed(self, packet):
        """Updates the internal state of the device when a packet arrives"""
        val = packet.data[1]
        self._is_on = val == 0x70
        # schedule_update_ha_state()
        print("VINCENT:  update light - light if on : %s" % (str(self._is_on)))
        self.schedule_update_ha_state()


class FUD14Entity(EltakoLightEntity):
    """Represents an Eltako FUD14 Light"""

    def __init__(self, device_id, device_name, sender_id):
        """Description"""
        super().__init__(device_id, device_name, sender_id)
        self._color_mode = ColorMode.ONOFF
        self.model = "FUD14"
        self._brightness = 77
        self._supported_color_modes = {ColorMode.BRIGHTNESS}
        self._color_mode = ColorMode.BRIGHTNESS

    def turn_on(self, **kwargs: Any) -> None:
        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None:
            self._brightness = brightness
        val = math.floor(self._brightness / 256.0 * 100.0)
        if val == 0:
            val = 1
        print("turn FUD14 on : %s (brightness %s)" % (str(val), self._brightness))
        data = [0xA5, 0x02, val, 0x00, 0x09]
        data.extend(self._sender_id)
        data.extend([0x00])

        # optional = [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00]
        optional = [0x00]
        optional.append(self.device_id)
        optional.append([0x00, 0x00])
        optional = []

        self.send_command(data, optional, 0x01)
        # don't set _is_on to true, wait for callback
        # self._is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        command = [0xA5, 0x02, 0x00, 0x00, 0x08]
        command.extend(self._sender_id)
        command.extend([0x00])

        optional = [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00]
        self.send_command(command, optional, 0x01)

        # don't set ._is_on to false, wait for callback
        # self._is_on = False

    @property
    def brightness(self):
        """Brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    def value_changed(self, packet):
        """Updates the internal state of the device when a packet arrives"""
        val = packet.data[2]
        self._is_on = bool(val != 0)
        if val != 0:
            self._brightness = math.floor(val * 256 / 100)
        # schedule_update_ha_state()
        print(
            "VINCENT:  update light - light if on : %s (%s%%)"
            % (str(self._is_on), str(val))
        )
        self.schedule_update_ha_state()
