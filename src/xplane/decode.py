import time
import socket
import struct

from bluesky.tools import aero

from plugins.flightsim.src.aircraft import FlightSimAircraft

def decode(msg, address):
    """
    Decode X-Plane 12 UDP message
    """
    header = msg[:5]
    nrow = (len(msg) - 5) // 36
    offset = 5
    for i in range(nrow):
        id = str(struct.unpack('h', msg[offset:offset+2])).strip('(),')
        info = struct.unpack('8f', msg[offset+4:offset+36])

        if id == '3': # Speeds
            tas = float(info[2]) * aero.kts       # [m/s]
        
        if id == '17': # Pitch, Roll and heading
            pitch = float(info[0])                          # [deg]
            roll = float(info[1])                           # [deg]
            heading = float(info[2])                        # [deg]

        if id == '18': # AoA, sideslip, path
            alpha = float(info[0])                          # [deg]
            beta = float(info[1])                           # [deg]
            gamma = float(info[3])                          # [deg]

        if id == '20': # Latitude, longitude & altitude
            latitude = float(info[0])                       # [deg]
            longitude = float(info[1])                      # [deg]
            altitude = float(info[2]) * aero.ft             # [m]

        if id == '104': # Transponder
            mode = int(info[0])                             # [-]
            squawk = int(info[1])                           # [-]
    
        offset += 36

    return FlightSimAircraft(address, simname="X-Plane 12", callsign='PHLAB', alpha=alpha, beta=beta, gamma=gamma,
                             phi=roll, theta=pitch, psi=heading, latitude=latitude, longitude=longitude, altitude=altitude, 
                             tas=tas)