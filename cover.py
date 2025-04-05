"""Support for EnOcean roller shutters."""
from __future__ import annotations

import asyncio
from enum import Enum
from math import ceil

from enocean.protocol.constants import RORG
from enocean.protocol.packet import PACKET
from enocean.utils import combine_hex, to_hex_string
import voluptuous as vol

from homeassistant.components.cover import (
    ATTR_POSITION,
    DEVICE_CLASSES_SCHEMA,
    PLATFORM_SCHEMA,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.const import CONF_DEVICE_CLASS, CONF_DEVICE_ID, CONF_ID, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import LOGGER, SIGNAL_SEND_MESSAGE
from .device import EltakoEntity

DEFAULT_NAME = "EnOcean roller shutter"

CONF_SENDER_ID = "sender_id"
CONF_DURATION = "duration"

WATCHDOG_TIMEOUT = 1
WATCHDOG_INTERVAL = 1
WATCHDOG_MAX_QUERIES = 10

COVER_OPEN = 0x01
COVER_CLOSE = 0x02
COVER_STOP = 0x00


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Required(CONF_SENDER_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Required(CONF_DURATION): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_DEVICE_CLASS): DEVICE_CLASSES_SCHEMA,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Cover platform for EnOcean."""
    device_id = config[CONF_DEVICE_ID]
    sender_id = config[CONF_SENDER_ID]
    device_name = config[CONF_NAME]
    device_class = config.get(CONF_DEVICE_CLASS)
    duration = int(config.get(CONF_DURATION)) * 10  # by 100 ms
    if device_class is None:
        device_class = CoverDeviceClass.BLIND

    cover = FSB14Entity(sender_id, device_id, device_name, duration, device_class)

    add_entities([cover])


class EnOceanCoverCommand(Enum):
    """The possible commands to be sent to an EnOcean cover."""

    SET_POSITION = 1
    STOP = 2
    QUERY_POSITION = 3
    OPEN_FULLY = 4
    CLOSE_FULLY = 5


class FSB14Entity(EltakoEntity, CoverEntity):
    """Representation of an EnOcean Cover (EEP D2-05-00)."""

    def __init__(self, sender_id, device_id, device_name, duration, device_class):
        """Initialize the EnOcean Cover."""
        super().__init__(device_id, device_name)
        self._attr_device_class = device_class
        self._sender_id = sender_id
        self._duration = duration
        self._position = None
        self._is_closed = None
        self._is_opening = False
        self._is_closing = False
        self._attr_name = device_name
        self._attr_unique_id = f"{combine_hex(device_id)}-{device_class}"
        self._stop_suspected = False
        self._attr_supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
            | CoverEntityFeature.SET_POSITION
        )
        self._is_opened = None

    @property
    def current_cover_position(self) -> int | None:
        """Return the current cover position."""
        return self._position

    @property
    def is_opening(self) -> bool | None:
        """Return if the cover is opening or not."""
        return self._is_opening

    @property
    def is_closing(self) -> bool | None:
        """Return if the cover is closing or not."""
        return self._is_closing

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed or not."""
        return self._is_closed

    async def async_added_to_hass(self):
        """Query status after Home Assistant (re)start."""
        await super().async_added_to_hass()
        # await self.hass.async_add_executor_job(self.start_or_feed_watchdog)

    def open_cover(self, **kwargs) -> None:
        """Open the cover."""
        self._is_opening = True
        self._is_closing = False
        self.send_telegram(EnOceanCoverCommand.OPEN_FULLY, 100)

    def close_cover(self, **kwargs) -> None:
        """Close the cover."""
        self._is_opening = False
        self._is_closing = True
        self.send_telegram(EnOceanCoverCommand.CLOSE_FULLY, 0)

    def set_cover_position(self, **kwargs) -> None:
        """Set the cover position."""

        LOGGER.debug("VINCENT : SET_COVER_POSITION %s" % (self._position))

        if kwargs[ATTR_POSITION] == self._position:
            self._is_opening = False
            self._is_closing = False
        elif kwargs[ATTR_POSITION] > self._position:
            self._is_opening = True
            self._is_closing = False
        elif kwargs[ATTR_POSITION] < self._position:
            self._is_opening = False
            self._is_closing = True

        self.send_telegram(EnOceanCoverCommand.SET_POSITION, kwargs[ATTR_POSITION])

    def stop_cover(self, **kwargs) -> None:
        """Stop any cover movement."""
        self._state_changed_by_command = True
        self._is_opening = False
        self._is_closing = False
        self.send_telegram(EnOceanCoverCommand.STOP)

    def value_changed(self, packet):
        """Fire an event with the data that have changed.
        This method is called when there is an incoming packet associated
        with this platform.
        """
        LOGGER.debug("FSB14 value changed2!")
        # position is inversed in Home Assistant and in EnOcean:
        # 0 means 'closed' in Home Assistant and 'open' in EnOcean
        # 100 means 'open' in Home Assistant and 'closed' in EnOcean
        LOGGER.debug("VINCENT cover data : %s", to_hex_string(packet.data))

        rorg = packet.data[0]
        
        # fsb 14 returns :
        # - 0xF6/RPS answer for closing, opening, fully closed and fully opened
        # - BS4 for teach in
        # - BS4 for stop position
        if rorg == RORG.BS4:
            new_duration = packet.data[2]
            direction = packet.data[3]  # Direction du mouvement
            
            # Calcul de la position en fonction de la direction
            if direction == 0x01:  # Ouverture
                self._position = (new_duration / self._duration * 100)
            else:  # Fermeture ou arrêt
                self._position = 100 - (new_duration / self._duration * 100)
            
            self._is_opening = False
            self._is_closing = False
            self._is_closed = (self._position == 0)

            LOGGER.debug("VINCENT : closed ? : %s (%s)" % (to_hex_string(packet.data[3]), packet.data[3]))
            LOGGER.debug("VINCENT : new duration : %s" % (new_duration))
            LOGGER.debug("VINCENT : direction : %s" % (direction))
            LOGGER.debug("VINCENT : new position : %s" % (self._position))
            LOGGER.debug("VINCENT : is_opening : %s" % (self._is_opening))
            LOGGER.debug("VINCENT : is_closing : %s" % (self._is_closing))
            LOGGER.debug("VINCENT : is_closed : %s" % (self._is_closed))

        elif rorg == RORG.RPS:
            position = packet.data[1]
            if position == 0x50:  # closed
                self._position = 0
                self._is_opening = False
                self._is_closing = False
                self._is_closed = True
                LOGGER.debug("VINCENT : RPS - Volet complètement fermé")
            elif position == 0x70:  # opened
                self._position = 100
                self._is_opening = False
                self._is_closing = False
                self._is_closed = False
                LOGGER.debug("VINCENT : RPS - Volet complètement ouvert")
            elif position == 0x02:  # closing
                self._is_opening = False
                self._is_closing = True
                self._is_closed = False  # Le volet n'est pas encore fermé
                LOGGER.debug("VINCENT : RPS - Volet en cours de fermeture")
            elif position == 0x01:  # opening
                self._is_opening = True
                self._is_closing = False
                self._is_closed = False  # Le volet n'est plus fermé puisqu'il commence à s'ouvrir
                LOGGER.debug("VINCENT : RPS - Volet en cours d'ouverture")
            else:
                LOGGER.warning("VINCENT : RPS - Valeur non comprise : %s", position)
                raise Exception("value not understood")

            LOGGER.debug("VINCENT : new position : %s" % (self._position))
            LOGGER.debug("VINCENT : is_opening : %s" % (self._is_opening))
            LOGGER.debug("VINCENT : is_closing : %s" % (self._is_closing))
            LOGGER.debug("VINCENT : is_closed : %s" % (self._is_closed))

        self.schedule_update_ha_state()

    def send_telegram(self, command: EnOceanCoverCommand, position: int = 0):
        # if self._position is None:
        #    self._position = 50

        # current_position = self._position if self._position is not None else 0

        if command == EnOceanCoverCommand.CLOSE_FULLY:
            direction = COVER_CLOSE
            diff_duration = self._duration
        elif command == EnOceanCoverCommand.OPEN_FULLY:
            direction = COVER_OPEN
            diff_duration = self._duration
        if command == EnOceanCoverCommand.SET_POSITION:
            if self._position is None:
                diff_duration = ceil(position / 100 * self._duration)
                if position < 50:
                    direction = COVER_CLOSE
                else:
                    direction = COVER_OPEN
            else:
                if position < self._position:
                    diff_duration = ceil(
                        (self._position - position) / 100 * self._duration
                    )
                    direction = COVER_CLOSE
                else:
                    diff_duration = ceil(
                        (position - self._position) / 100 * self._duration
                    )
                    direction = COVER_OPEN

            LOGGER.debug("VINCENT : diff_duration = %s" % (diff_duration))
            LOGGER.debug("VINCENT : new position = %s" % (position))
            LOGGER.debug("VINCENT : self._duration = %s" % (self._duration))
            # diff_duration = ceil(
            #     self._duration * (100 - abs(current_position - position)) / 100.0
            # )
            LOGGER.debug("VINCENT : diff_percentage : %s" % (diff_duration))
        elif command == EnOceanCoverCommand.STOP:
            direction = COVER_STOP
            diff_duration = 0

        # test

        data = [RORG.BS4, 0x00, diff_duration, direction, 0x0A]
        data.extend(self._sender_id)
        data.extend([0x00])  # status

        optional = []

        self.send_command(data, optional, PACKET.RADIO)
