""" Teach in module for eltako devices """
import queue
from time import time
from ..const import (
    LOGGER,
    SIGNAL_SEND_MESSAGE,
    TEACH_IN,
    TEACH_OUT
)
from ..utils import (
    get_communicator_reference,
    hex_list_to_str,
    str_to_hex_list,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_TYPE
from homeassistant.core import HomeAssistant, ServiceCall
from enocean.communicators import Communicator
from enocean.protocol.packet import RORG, Packet, PACKET
from homeassistant.helpers.dispatcher import dispatcher_send

TIMEOUT = 30

FSR14_TEACH_IN_DATA = [RORG.BS4, 0xE0, 0x40, 0x0D, 0x80]
FUD14_TEACH_IN_DATA = [RORG.BS4, 0xE0, 0x40, 0x0D, 0x80]
FSB14_TEACH_IN_DATA = [RORG.BS4, 0xFF, 0xF8, 0x0D, 0x80]
ELTAKO_TEACHIN_STATE = "eltako.teachin"


def teach(hass: HomeAssistant, in_or_out, sender_id, device_type):
    """Teach in or out a sender"""
    communicator: Communicator = get_communicator_reference(hass)

    # clear the receive-queue to only listen to new teach-in packets
    with communicator.receive.mutex:
        communicator.receive.queue.clear()

    if device_type == "FSR14":
        teachin_data = FSR14_TEACH_IN_DATA.copy()
    elif device_type == "FUD14":
        teachin_data = FUD14_TEACH_IN_DATA.copy()
    elif device_type == "FSB14":
        teachin_data = FSB14_TEACH_IN_DATA.copy()
    else:
        raise Exception('Unknow type "%s"' % (device_type))

    teachin_data.extend(sender_id)
    teachin_data.extend([0x00])

    LOGGER.info("Teachin_data : %s", str(teachin_data))

    optional = []
    packet = Packet(PACKET.RADIO, teachin_data, optional=optional)

    cb_to_restore = communicator._Communicator__callback

    communicator._Communicator__callback = None

    dispatcher_send(hass, SIGNAL_SEND_MESSAGE, packet)

    # async_dispatcher_connect(hass, SIGNAL_RECEIVE_MESSAGE, teachin_response)

    start_time = time()

    ack = False

    ack_data = [RORG.BS4, 0x01, 0x00, 0x00, 0x07]
    ack_data.extend(sender_id)
    ack_data.append(0x00)

    try:
        while time() < start_time + TIMEOUT:
            try:
                packet: Packet = communicator.receive.get(block=True, timeout=1)
                print("VINCENT : packet receive by teach in")

                if packet is None:
                    continue

                if packet.data == ack_data:
                    print("VINCENT : ack received")
                    ack = True
                    if in_or_out == TEACH_OUT:
                        communicator._Communicator__callback = cb_to_restore
                        return True
                    continue

                waited_response_data = [RORG.BS4]
                waited_response_data.extend(sender_id[1:])
                waited_response_data.append(0x08)

                print(
                    "VINCENT : compare teach-in responses : %s vs %s"
                    % (
                        hex_list_to_str(waited_response_data),
                        hex_list_to_str(packet.data[:5]),
                    )
                )

                if packet.data[:5] == waited_response_data:
                    if not ack:
                        print("VINCENT : response received but not ack")

                    device_id = packet.data[5:-1]
                    print(
                        "VINCENT : response OK. Device id : %s"
                        % (hex_list_to_str(device_id))
                    )
                    communicator._Communicator__callback = cb_to_restore
                    return device_id
            except queue.Empty:
                continue
    finally:
        print("VINCENT : restore communicator callback")
        communicator._Communicator__callback = cb_to_restore

    return None


def eltako_teachin(hass: HomeAssistant, service_call: ServiceCall):
    """Teach in a device with a given sender"""

    is_running_state = hass.states.get(ELTAKO_TEACHIN_STATE)
    if is_running_state is not None and is_running_state.state == "1":
        send_already_running_notification(hass)
        return False

    hass.states.set(ELTAKO_TEACHIN_STATE, "1")
    sender_id_str = service_call.data.get(CONF_DEVICE_ID).strip()
    sender_id = str_to_hex_list(sender_id_str)
    device_type = service_call.data.get(CONF_TYPE)
    LOGGER.info(
        "Eltako Teach in device %s (%s) of type %s",
        str(sender_id),
        sender_id_str,
        device_type,
    )

    device_id = teach(hass, TEACH_IN, sender_id, device_type)

    if device_id is None:
        message = "Eltako : teach-in failed for %s ! (timeout)" % (
            hex_list_to_str(sender_id)
        )
    else:
        message = "Eltako : device %s teached-in with device %s" % (
            hex_list_to_str(device_id),
            hex_list_to_str(sender_id),
        )

    hass.services.call(
        "persistent_notification",
        "create",
        service_data={
            "message": message,
            "title": "Result of TeachIn Service call",
        },
    )

    hass.states.set(ELTAKO_TEACHIN_STATE, "")

    return True


def eltako_teachout(hass: HomeAssistant, service_call: ServiceCall):
    """Teach out a device with a given sender"""

    is_running_state = hass.states.get(ELTAKO_TEACHIN_STATE)
    if is_running_state is not None and is_running_state.state == "1":
        send_already_running_notification(hass)
        return False

    hass.states.set(ELTAKO_TEACHIN_STATE, "1")
    sender_id_str = service_call.data.get(CONF_DEVICE_ID).strip()
    sender_id = str_to_hex_list(sender_id_str)
    device_type = service_call.data.get(CONF_TYPE)
    LOGGER.info(
        "Eltako Teach out device %s (%s) of type %s",
        str(sender_id),
        sender_id_str,
        device_type,
    )

    success = teach(hass, TEACH_OUT, sender_id, device_type)

    if success is None:
        message = "Eltako : teach-out failed for %s ! (timeout)" % (
            hex_list_to_str(sender_id)
        )
    else:
        message = "Eltako : device %s teached-out" % (hex_list_to_str(sender_id),)

    hass.services.call(
        "persistent_notification",
        "create",
        service_data={
            "message": message,
            "title": "Result of TeachOut Service call",
        },
    )

    hass.states.set(ELTAKO_TEACHIN_STATE, "")

    return True


def send_already_running_notification(hass: HomeAssistant):
    """Sends a notification to says that another teach in/out is already running"""
    message = "Another teach in/out is already running"
    hass.services.call(
        "persistent_notification",
        "create",
        service_data={
            "message": message,
            "title": "Result of Teach out/int Service call",
        },
    )
