#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Example on getting the information about the EnOcean controller.
The sending is happening between the application and the EnOcean controller,
no wireless communication is taking place here.
The command used here is specified as 1.10.5 Code 03: CO_RD_VERSION
in the ESP3 document.
"""

from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RORG
from enocean import utils
import traceback
import sys

try:
    import queue
except ImportError:
    import Queue as queue

init_logging()
"""
'/dev/ttyUSB0' might change depending on where your device is.
To prevent running the app as root, change the access permissions:
'sudo chmod 777 /dev/ttyUSB0'
"""
communicator = SerialCommunicator(port="/dev/ttyUSB0", callback=None)
packet = Packet(PACKET.COMMON_COMMAND, [0x03])
# packet = Packet(
#     PACKET.RADIO,
#     [0xA5, 0x0, 0x0, 0x0, 0x1, 0xFF, 0xEC, 0x90, 0x81, 0x0],
#     [0x0, 0xFF, 0xFF, 0xFF, 0xFF, 0x30, 0x0],
# )


communicator.daemon = True
communicator.start()
communicator.send(packet)

while communicator.is_alive():
    try:
        # print("olala")
        packet = communicator.receive.get(block=True, timeout=1)
        # print("recevied !!!")
        if packet.packet_type == PACKET.RESPONSE:
            print("data : ", packet.data)
            print("Return Code: %s" % utils.to_hex_string(packet.data[0]))
            print("APP version: %s" % utils.to_hex_string(packet.data[1:5]))
            print("API version: %s" % utils.to_hex_string(packet.data[5:9]))
            print("Chip ID: %s" % utils.to_hex_string(packet.data[9:13]))
            print("Chip Version: %s" % utils.to_hex_string(packet.data[13:17]))
            print("App Description Version: %s" % utils.to_hex_string(packet.data[17:]))
            print(
                "App Description Version (ASCII): %s" % str(bytearray(packet.data[17:]))
            )
        elif packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.VLD:
            packet.select_eep(0x05, 0x00)
            packet.parse_eep()
            for k in packet.parsed:
                print("%s: %s" % (k, packet.parsed[k]))
        elif packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS4:
            # parse packet with given FUNC and TYPE
            for k in packet.parse_eep(0x02, 0x05):
                print("%s: %s" % (k, packet.parsed[k]))
        elif packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS1:
            # alternatively you can select FUNC and TYPE explicitely
            packet.select_eep(0x00, 0x01)
            # parse it
            packet.parse_eep()
            for k in packet.parsed:
                print("%s: %s" % (k, packet.parsed[k]))
        elif packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.RPS:
            for k in packet.parse_eep(0x02, 0x02):
                print("%s: %s" % (k, packet.parsed[k]))
        else:
            print("Type : %s" % (packet.packet_type))
            print("RORG : %s" % (packet.rorg))

    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
