import time
import socket
import struct

from bluesky.tools import aero

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
# sock.bind(('192.168.1.128', 10002))

def decode(msg):
    """
    Decode X-Plane 12 UDP message
    """
    flight = {}
    header = msg[:5]
    nrow = (len(msg) - 5) // 36
    offset = 5
    for i in range(nrow):
        id = str(struct.unpack('h', msg[offset:offset+2])).strip('(),')
        info = struct.unpack('8f', msg[offset+4:offset+36])

        if id == '3': # Speeds
            airspeed_true = float(info[2]) * aero.kts   # [kts]
        
        if id == '17': # Pitch, Roll and heading
            pitch = float(info[0])
            roll = float(info[1])
            heading = float(info[2])

        if id == '18': # AoA, sideslip, path
            alpha = float(info[0])
            beta = float(info[1])
            gamma = float(info[3])

        if id == '20': # Latitude, longitude & altitude
            latitude = float(info[0])
            longitude = float(info[1])
            altitude = float(info[2])

        if id == '104': # Transponder
            mode = int(info[0])
            squawk = int(info[1])
    
        offset += 36

    timestamp = time.time()
    flight = {'ts': timestamp,
            'callsign': 'PHLAB',
            'squawk': squawk,
            'actype': 'B744',
            'ident': False,
            'altitude': altitude,
            'airspeed': airspeed_true,
            'vertical_speed': 0,
            'heading': heading,
            'latitude': latitude,
            'longitude': longitude}

    return flight

# while True:
#     data, address = sock.recvfrom(1024)
#     print(decode(data))