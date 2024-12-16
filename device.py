"""Representation of an eltako device"""
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RETURN_CODE
from enocean.utils import combine_hex, to_hex_string

from .utils import hex_list_to_str

from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import Entity, DeviceInfo
from .const import DOMAIN, SIGNAL_RECEIVE_MESSAGE, SIGNAL_SEND_MESSAGE, LOGGER

class EltakoEntity(Entity):
    """Parent class for all entities associated with this component"""

    def __init__(self, device_id, device_name) -> None:
        """Initialize"""
        self.device_id = device_id
        self.device_name = device_name
        self.manufacturer = "Eltako"
        self.model = None

    async def async_added_to_hass(self):
        """Register callback"""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_RECEIVE_MESSAGE, self._message_receive_callback
            )
        )

    def _message_receive_callback(self, packet):
        """Handle incoming packet"""

        if packet.packet_type == PACKET.RADIO_ERP1:
            LOGGER.debug(
                "VINCENT : packet compare %s vs %s (%s)"
                % (packet.sender_int, combine_hex(self.device_id),
                    hex_list_to_str(self.device_id))
            )
            if packet.sender_int == combine_hex(self.device_id):
                # LOGGER.debug("VINCENT : update value")
                self.value_changed(packet)
        else:
            LOGGER.debug(
                "Packet is not of type RADIO_ERP1. Type %s : ",
                to_hex_string([packet.packet_type]),
            )

    def value_changed(self, packet):
        """Updates the internal state of the device when a packet arrives"""

    def send_command(self, data, optional, packet_type):
        """Sends a command via the dongle"""

        packet = Packet(packet_type, data=data, optional=optional)
        dispatcher_send(self.hass, SIGNAL_SEND_MESSAGE, packet)

    @property
    def name(self):
        """Name of the entity."""
        return self.device_name

    @property
    def device_info(self):
        LOGGER.debug("VINCENT : device_info : " + str({
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.device_name,
            "manufacturer": self.manufacturer,
            "model": self.model,
        }))
        return DeviceInfo({
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.device_name,
            "manufacturer": self.manufacturer,
            "model": self.model
        })

    @property
    def unique_id(self):
        return combine_hex(self.device_id)
