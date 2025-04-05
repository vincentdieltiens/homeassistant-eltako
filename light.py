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
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from enocean.protocol.constants import PACKET, RORG

from .device import EltakoEntity
from .const import DOMAIN, LOGGER, CONF_SENDER_ID, DATA_ELTAKO
from .utils import hex_list_to_str

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_DEVICE_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Required(CONF_SENDER_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Optional(CONF_MODEL, default="F4SR14"): vol.In(["F4SR14", "FUD14"]),
    }
)

async def async_setup_platform(
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

    # if device_name == "SAM":
    #     config_entry_id = hass.data[DATA_ELTAKO]["config_entry_id"]
    #     device_reg = device_registry.async_get(hass)
    #     dev = device_reg.async_get_or_create(
    #         config_entry_id=config_entry_id,
    #         name=light.device_name,
    #         manufacturer=light.manufacturer,
    #         model=light.model,
    #         identifiers={(DOMAIN, light.unique_id)}
    #     )

    #     LOGGER.debug("VINCENT : entity id " + str(light.unique_id))
    #     LOGGER.debug("VINCENT : device id " + str(dev.id))

    #     ent_registry = entity_registry.async_get(hass)
    #     ent_registry.async_get_or_create(
    #         domain=DOMAIN,
    #         platform="homeassistant_elatko",
    #         unique_id=light.unique_id,
    #         original_icon="mdi:lightbulb",
    #         device_id=device.id
    #         #original_device_class="light",
    #         original_name=hex_list_to_str(light.device_id)
    #     )

# def async_setup_entry(
#     hass: HomeAssistant,
#     entry: ConfigEntry,
#     async_add_entities: AddEntitiesCallback
# ):
#     LOGGER.debug("VINCENT : Calling light.async_setup_entry entry=%s", entry)

#     device_id = [0x00, 0x00, 0x00, 0x00]
#     sender_id = [0x00, 0x00, 0x00, 0x00]
#     device_name = "Light_Test"
#     light = F4SR14Entity(device_id, device_name, sender_id)

#     async_add_entities([light], True)

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

        LOGGER.debug("VINCENT : DATA " + str(self.hass.data[DATA_ELTAKO]))

        # config_entry_id = self.hass.data[DATA_ELTAKO]["config_entry_id"]
        # device_reg = device_registry.async_get(self.hass)
        # device_reg.async_get_or_create(
        #     config_entry_id=config_entry_id,
        #     name=self.device_name,
        #     manufacturer=self.manufacturer,
        #     model=self.model,
        #     identifiers={(DOMAIN, self.unique_id)}
        # )

        # ent_registry = entity_registry.async_get(self.hass)
        # ent_registry.async_get_or_create(
        #     domain=DOMAIN,
        #     platform="homeassistant_elatko",
        #     unique_id=self.unique_id,
        #     original_icon="mdi:lightbulb",
        #     device_id=hex_list_to_str(self.device_id),
        #     #original_device_class="light",
        #     original_name=hex_list_to_str(self.device_id)
        # )


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
        
        # Valeurs observées avec l'interrupteur physique
        self._MIN_PHYSICAL_VALUE = 34  # Valeur minimale pour avoir de la lumière
        self._MAX_PHYSICAL_VALUE = 65  # Valeur maximale observée (0x41)

    def _calculate_dimming_value(self, brightness):
        """Calcule la valeur à envoyer au dimmer en fonction de la luminosité demandée"""
        if brightness == 0:
            LOGGER.debug(
                "VINCENT DIMMER : Demande d'extinction (brightness: 0)"
            )
            return 0
            
        # Convertir brightness (0-255) en valeur physique (MIN-MAX)
        physical_range = self._MAX_PHYSICAL_VALUE - self._MIN_PHYSICAL_VALUE
        dimming_value = self._MIN_PHYSICAL_VALUE + math.floor(brightness / 255.0 * physical_range)
        
        LOGGER.debug(
            "VINCENT DIMMER : Conversion brightness -> dimming : %d -> %d (plage physique: %d-%d)",
            brightness, dimming_value, self._MIN_PHYSICAL_VALUE, self._MAX_PHYSICAL_VALUE
        )
        
        return dimming_value

    def turn_on(self, **kwargs):
        """Turn the light on"""
        LOGGER.debug("VINCENT DIMMER : Appel turn_on avec kwargs: %s", kwargs)
        
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
            LOGGER.debug("VINCENT DIMMER : Nouvelle brightness demandée: %d", self._brightness)
            
        dimming_value = self._calculate_dimming_value(self._brightness)
        LOGGER.debug("VINCENT DIMMER : Envoi valeur gradation: %d%%", dimming_value)
        
        data = [0xA5, 0x02, dimming_value, 0x00, 0x09]
        data.extend(self._sender_id)
        data.extend([0x00])

        optional = [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00]
        self.send_command(data, optional, 0x01)
        
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        command = [0xA5, 0x02, 0x00, 0x00, 0x08]
        command.extend(self._sender_id)
        command.extend([0x00])

        optional = [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00]
        self.send_command(command, optional, 0x01)

    @property
    def brightness(self):
        """Brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    def value_changed(self, packet):
        """Updates the internal state of the device when a packet arrives"""
        LOGGER.debug(
            "VINCENT DIMMER : Paquet reçu - RORG: %s, Data: %s",
            hex(packet.rorg), [hex(x) for x in packet.data]
        )
        
        val = packet.data[2]
        self._is_on = bool(val != 0)
        
        if val != 0:
            if val < self._MIN_PHYSICAL_VALUE:
                # Si la valeur est en dessous du minimum, on considère que c'est 0%
                self._brightness = 0
            elif val >= self._MAX_PHYSICAL_VALUE:
                # Si la valeur est au-dessus du maximum, on considère que c'est 100%
                self._brightness = 255
            else:
                # Conversion linéaire de la valeur physique (MIN-MAX) vers brightness (0-255)
                physical_range = self._MAX_PHYSICAL_VALUE - self._MIN_PHYSICAL_VALUE
                normalized = (val - self._MIN_PHYSICAL_VALUE) / physical_range
                self._brightness = math.floor(normalized * 255)
                
            LOGGER.debug(
                "VINCENT DIMMER : Conversion inverse : %d -> %d (%.1f%% de la plage utile)",
                val, self._brightness, (val - self._MIN_PHYSICAL_VALUE) / physical_range * 100
            )
                
        LOGGER.debug(
            "VINCENT DIMMER : Mise à jour état - ON: %s, Valeur: %d, Brightness: %d",
            str(self._is_on), val, self._brightness
        )
        self.schedule_update_ha_state()
