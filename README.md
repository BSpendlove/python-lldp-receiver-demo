### Python LLDP Receiver Demo

This is a quick and dirty demo using Pythons socket and struct modules to export TLV data from LLDP packets.

example.py will listen for all ethernet frames and will pass it into the LLDP object (server.py). The LLDP class performs a stupid check for the Ethernet EtherType to match 0x88cc (LLDP or SNAP header) and is currently listening on the IEEE defined multicast address `01:80:c2:00:00:0e`. There are other MAC destinations that LLDP implementations will use but this works perfectly fine for a lab with a Cisco IOS switch (or even IOSv/IOS XRv).

The demo will only print out TLVs that I have decided to implement. Any non-implemented TLVs will just print the tlv-code, tlv-length and raw tlv-value encoded as the bytes. OrgSpecific TLVs will capture the OUI and Org Subcode but will not perform any additional tasks other than just converting the raw bytes for the org defined string to a string.

IEEE document for LLDP (802.1AB-2016 - IEEE Standard for Local and metropolitan area networks - Station and Media Access Control Connectivity Discovery) https://ieeexplore.ieee.org/document/7433915

Here is an example of some output connected to a Cisco 3750G-24T switch:
```
{'ChassisID': {'chassis_id_subtype': 'MAC address', 'chassis_id': '00:16:c8:86:51:80'}}
{'PortID': {'port_id_subtype': 'Interface name', 'port_id': 'Gi1/0/9'}}
{'TimeToLive': 120}
{'SystemName': 'csw01.network.w17bs.co.uk'}
{'SystemDescription': 'Cisco IOS Software, C3750 Software (C3750-IPBASEK9-M), Version 12.2(55)SE12, RELEASE SOFTWARE (fc2)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2017 by Cisco Systems, Inc.\nCompiled Thu 28-Sep-17 02:29 by prod_rel_team'}
{'PortDescription': 'GigabitEthernet1/0/9'}
{'SystemCapabilities': {'system_capabilities': {'Other': False, 'Repeater': False, 'Bridge': True, 'WLAN access point': False, 'Router': True, 'Telephone': False, 'DOCSIS cable device': False, 'Station only': False}, 'enabled_capabilities': {'Other': False, 'Repeater': False, 'Bridge': True, 'WLAN access point': False, 'Router': True, 'Telephone': False, 'DOCSIS cable device': False, 'Station only': False}}}
{'ManagementAddress': {'address_string_length': 5, 'address_subtype': 1, 'management_address': '10.4.20.2', 'interface_subtype': 'system port number', 'interface_number': 224, 'oid_length': 0, 'oid_string': None}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 1, 'tlv_raw_value': 'b"\\x00\'\\x04"'}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 5, 'tlv_raw_value': "b'WS-C3750G-24T (PowerPC405):L0'"}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 7, 'tlv_raw_value': "b'12.2(55)SE12'"}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 9, 'tlv_raw_value': "b'Cisco Systems, Inc.'"}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 10, 'tlv_raw_value': "b'WS-C3750G-24T'"}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 2, 'tlv_raw_value': "b'\\x01A\\xc5n'"}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 2, 'tlv_raw_value': "b'\\x02\\x80\\x00\\x00'"}}
{'OrgSpecificTLV': {'oui': '00:12:bb', 'org_subcode': 3, 'tlv_raw_value': "b'\\x02\\x03\\x02  '"}}
{'OrgSpecificTLV': {'oui': '00:80:c2', 'org_subcode': 1, 'tlv_raw_value': "b'\\x00\\xe0'"}}
{'OrgSpecificTLV': {'oui': '00:12:0f', 'org_subcode': 1, 'tlv_raw_value': "b'\\x03l\\x01\\x00\\x1e'"}}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 9, 'tlv-value': "b'\\x00\\x12\\x0f\\x01\\x03l\\x01\\x00\\x1e'"} # Just an example prior to me implementing OrgSpecificTLVs
{'EndOfLLDPDU': None}
```