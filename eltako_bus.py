"""EltakoHub"""

from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean.protocol.constants import RORG, PACKET
from enocean.consolelogger import init_logging
import enocean.utils
import traceback
import sys

try:
    import queue
except ImportError:
    import Queue as queue


class Packet:
    """Represents a packet to be sent to the bus"""

    rorg = RORG.RPS
    rorg_func = 0x02
    rorg_type = 0x01
    sender = None
    r_1 = 0
    e_b = 1
    r_2 = 0
    sa = 0
    t_21 = 0
    un = 0

    def __init__(self, sender, r_1=0, eb=1, r_2=0, sa=0, t_21=0, un=0) -> None:
        self.sender = sender
        self.r_1 = r_1
        self.eb = eb
        self.r_2 = r_2
        self.sa = sa
        self.t_21 = t_21
        self.un = un

    def build(self):
        """Build the radio packet to send to the bus"""
        return RadioPacket.create(
            rorg=self.rorg,
            rorg_func=self.rorg_func,
            rorg_type=self.rorg_type,
            sender=self.sender,
            R1=self.r_1,
            EB=self.eb,
            R2=self.r_2,
            SA=self.sa,
            T21=self.t_21,
            un=self.un,
        )


class EltakoBus:
    """Represents An eltako bus"""

    _serial_communicator = None

    def __init__(self) -> None:
        usb_path = "/dev/ttyUSB0"
        init_logging()
        self._serial_communicator = SerialCommunicator(usb_path)
        self._serial_communicator.start()
        print(
            "The Base ID of your module is %s."
            % enocean.utils.to_hex_string(self._serial_communicator.base_id)
        )

    def send(self, packet):
        """Sends a packet through the serial communicator"""
        self._serial_communicator.send(packet.build())

    def close(self):
        """Stops/Closes the communication with the serial communicator"""
        self._serial_communicator.stop()

    def listen(self):
        """lister for telegrams"""
        while self._serial_communicator.is_alive():
            try:
                # Loop to empty the queue...
                packet = self._serial_communicator.receive.get(block=True, timeout=1)
                if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.VLD:
                    packet.select_eep(0x05, 0x00)
                    packet.parse_eep()
                    for k in packet.parsed:
                        print("%s: %s" % (k, packet.parsed[k]))
                elif (
                    packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS4
                ):
                    # parse packet with given FUNC and TYPE
                    for k in packet.parse_eep(0x02, 0x05):
                        print("%s: %s" % (k, packet.parsed[k]))
                elif (
                    packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS1
                ):
                    # alternatively you can select FUNC and TYPE explicitely
                    packet.select_eep(0x00, 0x01)
                    # parse it
                    packet.parse_eep()
                    for k in packet.parsed:
                        print("%s: %s" % (k, packet.parsed[k]))
                elif (
                    packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.RPS
                ):
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

        if self._serial_communicator.is_alive():
            self._serial_communicator.stop()
