import socket
from server import LLDP

ETH_P_ALL = 0x0003
SOCKET = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))

while True:
    data, address = SOCKET.recvfrom(65565)
    lldp = LLDP(data)
