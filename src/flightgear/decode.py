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
    timestamp = time.time()
    callsign = str(decoded[0])
    squawk = str(decoded[1]),
    actype  = str(decoded[2]),
    ident = bool(int(decoded[5])),
    altitude = int(decoded[6]),
    tas = int(decoded[7]),
    vs = float(decoded[8]),
    heading = float(decoded[9]),
    latitude = float(decoded[10]),
    longitude = float(decoded[11])

    return FlightSimAircraft(address, simname="FlightGear", callsign=callsign, alpha=0.0, beta=0.0, gamma=0.0,
                             phi=0.0, theta=0.0, psi=heading, latitude=latitude, longitude=longitude, altitude=altitude, 
                             tas=tas, vs=vs)