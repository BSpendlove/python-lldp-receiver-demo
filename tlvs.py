from struct import unpack
import ipaddress


class TLV:
    """The Port ID TLV is a mandatory TLV that identifies the port component of the MSAP identifier associated
    with the transmitting LLDP agent.
    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |     TLV Information String..  |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

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


class EndOfLLDPDU(TLV):
    """The End Of LLDPDU TLV is a 2-octet, all-zero TLV that is used to mark the end of the TLV sequence in
    LLDPDUs.

    0                   1
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MIN_LENGTH = 0
    MAX_LENGTH = 0

    def __init__(self, type_code, length, value, name="EndOfLLDPDU"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        return {self.name: None}


class ChassisID(TLV):
    """The Chassis ID TLV is a mandatory TLV that identifies the chassis containing the IEEE 802 LAN station
    associated with the transmitting LLDP agent.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |Chassis ID sub.|   Chassis ID  |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

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
    """The Port ID TLV is a mandatory TLV that identifies the port component of the MSAP identifier associated
    with the transmitting LLDP agent.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |port ID subtype|    port ID    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

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
    """The Time To Live TLV indicates the number of seconds that the recipient LLDP agent is to regard the
    information associated with this MSAP identifier to be valid.
    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |          time to live         |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

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


class PortDescription(TLV):
    """The Port Description TLV allows network management to advertise the IEEE 802 LAN station’s port
    description.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |        port description       |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MIN_LENGTH = 0
    MAX_LENGTH = 255

    def __init__(self, type_code, length, value, name="PortDescription"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        port_description = unpack(f"!{self.length}s", self.value)[0]

        return {self.name: port_description.decode("utf-8")}


class SystemName(TLV):
    """The System Name TLV allows network management to advertise the system’s assigned name.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |          system name          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MIN_LENGTH = 0
    MAX_LENGTH = 255

    def __init__(self, type_code, length, value, name="SystemName"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        system_name = unpack(f"!{self.length}s", self.value)[0]

        return {self.name: system_name.decode("utf-8")}


class SystemDescription(TLV):
    """The System Description TLV allows network management to advertise the system’s description.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |       system description      |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MIN_LENGTH = 0
    MAX_LENGTH = 255

    def __init__(self, type_code, length, value, name="SystemDescription"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        system_description = unpack(f"!{self.length}s", self.value)[0]

        return {self.name: system_description.decode("utf-8")}


class SystemCapabilities(TLV):
    """The System Capabilities TLV is an optional TLV that identifies the primary function(s) of the system and
    whether or not these primary functions are enabled.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |system capabil.| enabled capab.|
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MIN_LENGTH = 4
    MAX_LENGTH = 4

    CAPABILITIES_BITMAP = {
        0: "Other",
        1: "Repeater",
        2: "Bridge",
        3: "WLAN access point",
        4: "Router",
        5: "Telephone",
        6: "DOCSIS cable device",
        7: "Station only",
    }

    def __init__(self, type_code, length, value, name="SystemCapabilities"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        system_capabilities, enabled_capabilites = unpack("!HH", self.value)
        system_capabilities = reversed(
            [char for char in f"{system_capabilities:#010b}"[2:]]
        )
        enabled_capabilites = reversed(
            [char for char in f"{enabled_capabilites:#010b}"[2:]]
        )

        results = {"system_capabilities": {}, "enabled_capabilities": {}}

        for index, (s_capability, e_capability) in enumerate(
            zip(system_capabilities, enabled_capabilites)
        ):
            results["system_capabilities"].update(
                {self.CAPABILITIES_BITMAP[index]: (int(s_capability) == 1)}
            )
            results["enabled_capabilities"].update(
                {self.CAPABILITIES_BITMAP[index]: (int(e_capability) == 1)}
            )
        return {self.name: results}


class ManagementAddress(TLV):
    """The Management Address TLV identifies an address associated with the local LLDP agent that may be used
    to reach higher layer entities to assist discovery by network management.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |management add.| management ad.|
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | management ad.| interface num.|        interface number       |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                               | OID string le.| object identi.|
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MIN_LENGTH = 9
    MAX_LENGTH = 167

    def __init__(self, type_code, length, value, name="ManagementAddress"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        mgmt_addr_str_len = unpack("!B", self.value[:1])[
            0
        ]  # Length of Address Subtype + Address String
        mgmt_addr_subtype, mgmt_addr = unpack(
            f"!B{mgmt_addr_str_len - 1}s", self.value[1 : mgmt_addr_str_len + 1]
        )

        if mgmt_addr_subtype == 1:  # IPv4
            mgmt_addr = ipaddress.IPv4Address(mgmt_addr)
        elif mgmt_addr_subtype == 2:  # IPv6
            mgmt_addr = ipaddress.IPv6Address(mgmt_addr)
        else:  # Who cares...?
            pass

        interface_subtypes = {
            0: "Reserved",
            1: "Unknown",
            2: "ifIndex",
            3: "system port number",
        }

        interface_subtype, interface = unpack(
            "!Bl", self.value[mgmt_addr_str_len + 1 : mgmt_addr_str_len + 6]
        )

        if interface_subtype == 0 and interface > 0:
            raise ValueError(
                "Interface Index field must be 0 when interface_subtype field is Unknown. Bad implemention on vendor side..."
            )

        interface_subtype = interface_subtypes[interface_subtype]
        oid_length = unpack(
            "!B", self.value[mgmt_addr_str_len + 6 : mgmt_addr_str_len + 7]
        )[0]
        oid_string = None
        if oid_length:
            oid_string = unpack(
                f"!{oid_length}s",
                self.value[mgmt_addr_str_len + 7 : mgmt_addr_str_len + 7 + oid_length],
            )

        return {
            self.name: {
                "address_string_length": mgmt_addr_str_len,
                "address_subtype": mgmt_addr_subtype,
                "management_address": str(mgmt_addr),
                "interface_subtype": interface_subtype,
                "interface_number": interface,
                "oid_length": oid_length,
                "oid_string": oid_string if not oid_string else str(oid_string),
            }
        }

class OrgSpecificTLV(TLV):
    """The Management Address TLV identifies an address associated with the local LLDP agent that may be used
    to reach higher layer entities to assist discovery by network management.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Type    |      Length     |management add.| management ad.|
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | management ad.| interface num.|        interface number       |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                               | OID string le.| object identi.|
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MIN_LENGTH = 4
    MAX_LENGTH = 511

    def __init__(self, type_code, length, value, name="OrgSpecificTLV"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"LLDP Value {self.name} expected length should be no greater than {self.MAX_LENGTH} bytes."
            )

        oui, org_subtype = unpack("!3sB", self.value[:4])

        return {
            self.name : {
                "oui": oui.hex(":"),
                "org_subcode": org_subtype,
                "tlv_raw_value": str(self.value[4:])
            }
        }


class TLVNotImplemented(TLV):
    """Generic class for TLVs not implemented or reserved."""

    def __init__(self, type_code, length, value, name="TLVNotImplementedInCode"):
        super().__init__(type_code=type_code, length=length, value=value, name=name)

    def decode(self):
        return {
            "tlv-not-implemented": True,
            "tlv-code": self.type_code,
            "tlv-length": self.length,
            "tlv-value": str(self.value),
        }


TYPE_CODES = {
    0: EndOfLLDPDU,
    1: ChassisID,
    2: PortID,
    3: TimeToLive,
    4: PortDescription,
    5: SystemName,
    6: SystemDescription,
    7: SystemCapabilities,
    8: ManagementAddress,
    127: OrgSpecificTLV
}
