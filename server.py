import struct
from tlvs import TLV


class LLDP:
    LLDP_MULTICAST = "01:80:c2:00:00:0e"
    LLDP_ETHERTYPE = b"\x88\xCC"

    def __init__(self, data):
        self.decoded_data = []
        self.decode(data)

    def decode(self, data):
        # Check if EtherType is not correct IEEE EtherType (LLDP/SNAP)
        if not data[12:14] == self.LLDP_ETHERTYPE:
            return

        ether_header = data[:14]  # dst, src, etherType
        ether_unpacked = struct.unpack("!6s6sH", ether_header)

        # Check if Destination MAC is not correct IEEE defined multicast address
        dst = ether_unpacked[0].hex(":")
        if not dst == self.LLDP_MULTICAST:
            return

        lldp_frame = data[14:]
        lldp_tlvs = []
        while lldp_frame:
            tlv_headers = struct.unpack("!H", lldp_frame[:2])[0]
            tlv_code = tlv_headers >> 9
            tlv_length = tlv_headers & 0x01FF
            tlv_data = lldp_frame[2 : 2 + tlv_length]

            # lldp_tlvs.append(TLV(tlv_code, tlv_length, tlv_data).decode())
            print(TLV(tlv_code, tlv_length, tlv_data).decode())
            lldp_frame = lldp_frame[2 + tlv_length :]
