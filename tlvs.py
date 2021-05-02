from struct import unpack


class TLV:
    #   0                   1                   2                   3
    #   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   |     Type    |      Length     |     TLV Information String..  |
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    MIN_LENGTH = 0  # End Of LLDPDU TLV
    MAX_LENGTH = 511  # Excluding Type and Length fields

    def __init__(self, type_code, length, value, name=None):
        self.type_code = type_code
        self.length = length
        self.value = value
        self.name = name
        self.validate_length()

    def validate_length(self):
        # TLV Type + Length is always 2 Octets
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value is either lower than {self.MINIMUM_LENGTH} or greater than {self.MAX_LENGTH}"
            )

    def _decode(self):
        return self.decode()

    def decode(self):
        if not self.type_code in TYPE_CODES:
            # Type code not implemented
            return TLVNotImplemented(self.type_code, self.length, self.value).decode()

        tlv_object = TYPE_CODES[self.type_code]
        if not tlv_object:
            return None

        decode = getattr(
            tlv_object(self.type_code, self.length, self.value), "decode", None
        )
        if callable(decode):
            return decode()
        return None


class ChassisID(TLV):
    #   0                   1                   2                   3
    #   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   |     Type    |      Length     |Chassis ID sub.|   Chassis ID  |
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    MIN_LENGTH = 1
    MAX_LENGTH = 256

    def __init__(self, type_code, length, value, name="ChassisID"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        chassis_id_subtype, chassis_id = unpack("!B6s", self.value)

        subtypes = {
            0: "Reserved",
            1: "Chassis component",
            2: "Interface Alias",
            3: "Port component",
            4: "MAC address",
            5: "Network address",
            6: "Interface name",
            7: "Locally assigned",
        }

        if not chassis_id_subtype in subtypes:
            return {
                "Reserved": {
                    "chassis_id_subtype": subtypes[chassis_id_subtype],
                    "chassis_id": chassis_id.hex(),
                }
            }

        return {
            self.name: {
                "chassis_id_subtype": subtypes[chassis_id_subtype],
                "chassis_id": chassis_id.hex(":")
                if chassis_id_subtype == 4
                else chassis_id.hex(),
            }
        }


class PortID(TLV):
    #   0                   1                   2                   3
    #   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   |     Type    |      Length     |port ID subtype|    port ID    |
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    MIN_LENGTH = 1
    MAX_LENGTH = 255

    def __init__(self, type_code, length, value, name="PortID"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        port_id_subtype, port_id = unpack(f"!B{len(self.value) - 1}s", self.value)

        subtypes = {
            0: "Reserved",
            1: "Interface alias",
            2: "Port component",
            3: "MAC address",
            4: "Network address",
            5: "Interface name",
            6: "Agent circuit ID",
            7: "Locally assigned",
        }

        if not port_id_subtype in subtypes:
            return {
                "Reserved": {
                    "port_id_subtype": subtypes[port_id_subtype],
                    "port_id": port_id.decode("utf-8"),
                }
            }

        return {
            self.name: {
                "port_id_subtype": subtypes[port_id_subtype],
                "port_id": port_id.decode("utf-8"),
            }
        }


class TimeToLive(TLV):
    #   0                   1                   2                   3
    #   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   |     Type    |      Length     |          time to live         |
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    MIN_LENGTH = 2
    MAX_LENGTH = 2

    def __init__(self, type_code, length, value, name="TimeToLive"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        time_to_live = unpack(f"!H", self.value)[0]
        return {self.name: time_to_live}


class TLVNotImplemented(TLV):
    def __init__(self, type_code, length, value, name="TLVNotImplementedInCode"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        return {
            "tlv-not-implemented": True,
            "tlv-code": self.type_code,
            "tlv-length": self.length,
            "tlv-value": str(self.value),
        }


TYPE_CODES = {1: ChassisID, 2: PortID, 3: TimeToLive}
