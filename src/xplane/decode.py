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


    aircraft = {}
    for i in range(nrow):
        id = str(struct.unpack('h', msg[offset:offset+2])).strip('(),')
        info = struct.unpack('8f', msg[offset+4:offset+36])

        if id == '3': # Speeds
            aircraft['tas'] = float(info[2]) * aero.kts       # [m/s]
        
        if id == '17': # Pitch, Roll and heading
            aircraft['pitch'] = float(info[0])                          # [deg]
            aircraft['roll'] = float(info[1])                           # [deg]
            aircraft['yaw'] = float(info[2])                            # [deg]

        if id == '18': # AoA, sideslip, path
            aircraft['alpha'] = float(info[0])                          # [deg]
            aircraft['beta'] = float(info[1])                           # [deg]
            aircraft['gamma'] = float(info[3])                          # [deg]

        if id == '20': # Latitude, longitude & altitude
            aircraft['latitude'] = float(info[0])                       # [deg]
            aircraft['longitude'] = float(info[1])                      # [deg]
            aircraft['altitude'] = float(info[2] * aero.ft)             # [m]

        if id == '104': # Transponder
            aircraft['mode'] = int(info[0])                             # [-]
            aircraft['squawk'] = int(info[1])                           # [-]
    
        offset += 36

    return FlightSimAircraft(address, simname="X-Plane 12", callsign='PHXPL', type='B744', alpha=aircraft.get('alpha'), beta=aircraft.get('beta'), gamma=aircraft.get('gamma'),
                             phi=aircraft.get('roll'), theta=aircraft.get('pitch'), psi=aircraft.get('yaw'), latitude=aircraft.get('latitude'), longitude=aircraft.get('longitude'),
                             altitude=aircraft.get('altitude'), tas=aircraft.get('tas'), vs=0.0)