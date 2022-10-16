"""handle USB EnOcean Dongle"""
import glob

from os.path import basename, normpath

from enocean.communicators import SerialCommunicator
from serial import SerialException
from .const import LOGGER, SIGNAL_RECEIVE_MESSAGE, SIGNAL_SEND_MESSAGE

from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send


class EnOceanDongle:
    """Representation of en EnOcean dongle"""

    def __init__(self, hass, serial_path) -> None:
        """Initialize the dongle"""
        print("initialize dongle")
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
        self.dispatcher_disconnect_handle = async_dispatcher_connect(
            self.hass, SIGNAL_SEND_MESSAGE, self._send_message_callback
        )

    def _send_message_callback(self, command):
        """Sends a command through the EnOcean dongle"""
        self._communicator.send(command)

    def send_message(self, command):
        """Sends a command through the EnOcean dongle (public)"""
        self._communicator.send(command)

    @property
    def communicator(self):
        """Sets the communicator"""
        return self._communicator

    def callback(self, packet):
        """handle a packet received by the dongle"""
        print("packet received")
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
