"""Constants for the eltako integration."""
import logging

from homeassistant.const import Platform

DOMAIN = "homeassistant_eltako"
DATA_ELTAKO = "homeassistant_eltako"

SIGNAL_SEND_MESSAGE = "eltako.send_message"
SIGNAL_RECEIVE_MESSAGE = "eltako.receive_message"
ERROR_INVALID_DONGLE_PATH = "invalid_device"

LOGGER = logging.getLogger(__package__)

PLATFORMS = [Platform.LIGHT]

TEACH_IN = "teach_in"
TEACH_OUT = "teach_out"

CONF_SENDER_ID = "sender_id"
CONF_DELAY = "delay"