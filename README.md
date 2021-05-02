### Python LLDP Receiver Demo

This is a quick and dirty demo using Pythons socket and struct modules to export TLV data from LLDP packets.

example.py will listen for all ethernet frames and will pass it into the LLDP object (server.py). The LLDP class performs a stupid check for the Ethernet EtherType to match 0x88cc (LLDP or SNAP header) and is currently listening on the IEEE defined multicast address `01:80:c2:00:00:0e`. There are other MAC destinations that LLDP implementations will use but this works perfectly fine for a lab with a Cisco IOS switch (or even IOSv/IOS XRv).

The demo will only print out TLVs that I have decided to implement (3 mandatory TLVs which are 1, 2 and 3... however End of LLDPDU TLV should also be implemented as this is considered a mandatory TLV that should exist on all LLDP packets on the end of the message). Any non-implemented TLVs will just print the tlv-code, tlv-length and raw tlv-value encoded as the bytes.

IEEE document for LLDP (802.1AB-2016 - IEEE Standard for Local and metropolitan area networks - Station and Media Access Control Connectivity Discovery) https://ieeexplore.ieee.org/document/7433915

Here is an example of some output connected to a Cisco 3750G-24T switch:
```
{'ChassisID': {'chassis_id_subtype': 'MAC address', 'chassis_id': '00:16:c8:86:51:80'}}
{'PortID': {'port_id_subtype': 'Interface name', 'port_id': 'Gi1/0/9'}}
{'TimeToLive': 120}
{'tlv-not-implemented': True, 'tlv-code': 5, 'tlv-length': 25, 'tlv-value': "b'csw01.brandonspendlove.co.uk'"}
{'tlv-not-implemented': True, 'tlv-code': 6, 'tlv-length': 244, 'tlv-value': "b'Cisco IOS Software, C3750 Software (C3750-IPBASEK9-M), Version 12.2(55)SE12, RELEASE SOFTWARE (fc2)\\nTechnical Support: http://www.cisco.com/techsupport\\nCopyright (c) 1986-2017 by Cisco Systems, Inc.\\nCompiled Thu 28-Sep-17 02:29 by prod_rel_team'"}
{'tlv-not-implemented': True, 'tlv-code': 4, 'tlv-length': 20, 'tlv-value': "b'GigabitEthernet1/0/9'"}
{'tlv-not-implemented': True, 'tlv-code': 7, 'tlv-length': 4, 'tlv-value': "b'\\x00\\x14\\x00\\x14'"}
{'tlv-not-implemented': True, 'tlv-code': 8, 'tlv-length': 12, 'tlv-value': "b'\\x05\\x01\\n\\x04\\x14\\x02\\x03\\x00\\x00\\x00\\xe0\\x00'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 7, 'tlv-value': 'b"\\x00\\x12\\xbb\\x01\\x00\'\\x04"'}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 33, 'tlv-value': "b'\\x00\\x12\\xbb\\x05WS-C3750G-24T (PowerPC405):L0'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 16, 'tlv-value': "b'\\x00\\x12\\xbb\\x0712.2(55)SE12'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 23, 'tlv-value': "b'\\x00\\x12\\xbb\\tCisco Systems, Inc.'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 17, 'tlv-value': "b'\\x00\\x12\\xbb\\nWS-C3750G-24T'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 8, 'tlv-value': "b'\\x00\\x12\\xbb\\x02\\x01A\\xc5n'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 8, 'tlv-value': "b'\\x00\\x12\\xbb\\x02\\x02\\x80\\x00\\x00'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 9, 'tlv-value': "b'\\x00\\x12\\xbb\\x03\\x02\\x03\\x02  '"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 6, 'tlv-value': "b'\\x00\\x80\\xc2\\x01\\x00\\xe0'"}
{'tlv-not-implemented': True, 'tlv-code': 127, 'tlv-length': 9, 'tlv-value': "b'\\x00\\x12\\x0f\\x01\\x03l\\x01\\x00\\x1e'"}
{'tlv-not-implemented': True, 'tlv-code': 0, 'tlv-length': 0, 'tlv-value': "b''"}
```