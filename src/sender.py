import socket
import time
import threading
import numpy as np
from math import degrees

from bluesky import traf, settings

from plugins.flightsim.src.flightgear.encode import create_packet

class FlightSimSender():
    """
    BlueSky -> Flightsim traffic sender
    """
    def __init__(self):
        self.is_sending = False
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.daemon = True

    def start(self):
        self.is_sending = True
        self.send_thread.start()

    def send(self):
        while True:
            if not self.is_sending:
                time.sleep(1.0)
                continue
            else:
                for callsign in traf.id:
                    # Send package w.r.t flightsim traffic protocol back to the simulator
                    if callsign != 'PHFGS':
                        idx = traf.id2idx(callsign)
                        actype = traf.type[idx]
                        latitude = traf.lat[idx]
                        longitude = traf.lon[idx]
                        airspeed = traf.tas[idx]
                        altitude = traf.alt[idx]
                        heading = traf.hdg[idx]
                        #bank = degrees(traf.perf.bank[idx]) * -np.sign((traf.aporasas.hdg - heading + 180) % 360 - 180)[1]
                        vertical_speed = traf.vs[idx]
                        accel_x = traf.ax[idx]
                        packet = create_packet(callsign, actype, latitude, longitude, airspeed, altitude, phi=0.0, theta=0.0, psi=heading)
                        self.send_socket.sendto(packet, ('localhost', settings.flightgear_multiplay_in_port))