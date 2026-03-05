import time
import socket
import struct

from bluesky.tools import aero

from plugins.flightsim.src.aircraft import FlightSimAircraft

def decode(msg, address):
    """
    Decode FlightGear UDP message
    """
    decoded = msg.decode('utf-8').replace('"', '').split(";")
    aircraft = {'callsign': str(decoded[0]),
                'squawk': str(decoded[1]),
                'actype': str(decoded[2]),
                'ident': bool(int(decoded[3])),
                'altitude': int(decoded[4]),
                'tas': int(decoded[5]),
                'vs': float(decoded[6]),
                'yaw': float(decoded[7]),
                'latitude': float(decoded[8]),
                'longitude': float(decoded[9])}

    return FlightSimAircraft(address, simname="FlightGear", callsign='PHFGS', type=aircraft.get('actype'), alpha=0.0, beta=0.0, gamma=0.0,
                             phi=0.0, theta=0.0, psi=aircraft.get('yaw'), latitude=aircraft.get('latitude'), longitude=aircraft.get('longitude'),
                             altitude=aircraft.get('altitude'), tas=aircraft.get('tas'), vs=0.0)