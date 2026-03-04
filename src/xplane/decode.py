import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind(('192.168.1.128', 10002))

def decode(buffer):
    """
    Decode X-Plane 12 message
    """
    data = {}
    header = buffer[:5]

    id = str(struct.unpack('h', buffer[5:7])).strip('(),')
    print(len(buffer[7:39]))
    data = struct.unpack('8f', buffer[9:41])
    print(id, data)

    if id == '104': # Transponder
        mode = int(data[0])
        squawk = int(data[1])
        print(mode, squawk)

    return data

while True:
    data, address = sock.recvfrom(1024)
    decode(data)