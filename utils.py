"""Hold utility functions."""
from __future__ import annotations

import logging
from tkinter.ttk import Separator

from enocean.communicators import Communicator

# import DATA_ENOCEAN, ENOCEAN_DONGLE, EnOceanDongle
from homeassistant.core import HomeAssistant
from .const import DATA_ELTAKO
from .dongle import EnOceanDongle

LOGGER = logging.getLogger(__name__)


def get_communicator_reference(hass: HomeAssistant) -> object | Communicator:
    """Get a reference to the communicator (dongle/pihat)."""
    enocean_data = hass.data.get(DATA_ELTAKO, {})
    dongle: EnOceanDongle = enocean_data["dongle"]
    if not dongle:
        LOGGER.error("No EnOcean Dongle configured or available. No teach-in possible")
        return None
    communicator: Communicator = dongle.communicator
    return communicator


def str_to_hex_list(value: str, separator: str = "-"):
    """Convert an string to list of values. The input should be a string of hex values separated with dashes like FF-FF-FF-FF"""
    # "FF-D9-7F-81" => [255, 217,127, 129]
    reval = [int(x, 16) for x in value.split(separator)]
    return reval


def hex_list_to_str(value: list, separator: str = "-"):
    """Convert an string to list of values. The input should be a string of hex values separated with dashes like FF-FF-FF-FF"""
    # "FF-D9-7F-81" => [255, 217,127, 129]
    reval = separator.join([("%02X" % x) for x in value])
    return reval


def int_to_list(int_value):
    """Convert integer to list of values."""
    result = []
    while int_value > 0:
        result.append(int_value % 256)
        int_value = int_value // 256
    result.reverse()
    return result


def hex_to_list(hex_list):
    """Convert hexadecimal list to a list of int values."""
    # [0xFF, 0xD9, 0x7F, 0x81] => [255, 217, 127, 129]
    result = []
    if hex_list is None:
        return result

    for hex_value in hex_list:
        result.append(int(hex_value))
    result.reverse()
    return result
