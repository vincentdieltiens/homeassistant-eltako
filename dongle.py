"""handle USB EnOcean Dongle"""
import glob

from os.path import basename, normpath

from enocean.communicators import SerialCommunicator
from enocean.utils import to_hex_string
from serial import SerialException
from .const import LOGGER, SIGNAL_RECEIVE_MESSAGE, SIGNAL_SEND_MESSAGE

from enocean.protocol.constants import PACKET, RETURN_CODE
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from enocean.consolelogger import init_logging


class EnOceanDongle:
    """Representation of en EnOcean dongle"""

    def __init__(self, hass, serial_path) -> None:
        """Initialize the dongle"""
        print("initialize dongle")
        init_logging()
        self._communicator = SerialCommunicator(
            port=serial_path, callback=self.callback
        )
        self.serial_path = serial_path
        self.identifier = basename(normpath(serial_path))
        self.hass = hass
        self.dispatcher_disconnect_handle = None

    async def async_setup(self):
        """Finish the setup of the brigde and supported platforms"""
        self._communicator.start()
        print("GET ID : %s" % (self._communicator.base_id))
        self.dispatcher_disconnect_handle = async_dispatcher_connect(
            self.hass, SIGNAL_SEND_MESSAGE, self._send_message_callback
        )

    def _send_message_callback(self, packet):
        """Sends a packet through the EnOcean dongle"""
        print(
            "VINCENT : send packet %s, data=%s, optional=%s"
            % (
                to_hex_string(packet.packet_type),
                to_hex_string(packet.data),
                to_hex_string(packet.optional),
            )
        )
        self._communicator.send(packet)

    def send_message(self, packet):
        self._send_message_callback(packet)

    @property
    def communicator(self):
        """Sets the communicator"""
        return self._communicator

    def callback(self, packet):
        """handle a packet received by the dongle"""
        print(
            "VINCENT : packet received ; %s, data=%s, optional=%s"
            % (
                to_hex_string(packet.packet_type),
                to_hex_string(packet.data),
                to_hex_string(packet.optional),
            )
        )
        if packet.packet_type == PACKET.RESPONSE:  # anwer
            print("VINCENT : packet is response")
            return_code = packet.data[0]
            if (
                return_code == RETURN_CODE.ERROR
                or return_code == RETURN_CODE.NOT_SUPPORTED
            ):
                print("VINCENT : error !")

        dispatcher_send(self.hass, SIGNAL_RECEIVE_MESSAGE, packet)

    def unload(self):
        """Disconnect callbacks established at init time."""
        if self.dispatcher_disconnect_handle:
            self.dispatcher_disconnect_handle()
            self.dispatcher_disconnect_handle = None


def detect():
    """Reurn a list of candidate paths for USB EnOcean dongles"""
    globs = ["/dev/tty[A-Z][A-Z]*", "/dev/serial/by-id/*EnOcean*"]
    paths = []
    for current_glob in globs:
        paths.extend(glob.glob(current_glob))

    return paths


def validate_path(path: str):
    """return true if the provided path points to a valid serial port. False otherwise"""
    try:
        SerialCommunicator(port=path)
        return True
    except SerialException as exception:
        LOGGER.warning("Dongle path %s is invalid: %s", path, str(exception))
        return False
