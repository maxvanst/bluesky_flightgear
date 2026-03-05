"""
============================================================
|                                                          |
|             BlueSky Flight Simulator plugin              |
|                 FlightGear & X-Plane 12                  |
|                                                          | 
|               M.J. van Stuijvenberg, 2026                |
|        Delft University of Technology (TU Delft)         |
|            Faculty of Aerospace Engineering              |
|                                                          |
|          M.J.vanStuijvenberg@student.tudelft.nl          |
|                                                          |
============================================================
"""
import json
import time
import socket
import threading
import numpy as np

from bluesky.core import Entity
from bluesky import core, stack, traf, settings
from bluesky.tools import aero

from plugins.flightsim.src.aircraft import FlightSimAircraft
from plugins.flightsim.src.flightgear.decode import decode as FlightGearDecoder
from plugins.flightsim.src.xplane.decode import decode as XPlaneDecoder
from plugins.flightsim.src.flightgear.encode import create_packet as FlightGearPacket

def init_plugin():
    version = json.load(open('./plugins/flightsim/version.json', 'r')).get('version')
    plugin = FlightSimulatorPlugin(version)
    config = {
        'plugin_name': 'FLIGHTSIM',
        'plugin_type': 'sim'
    }
    return config

class FlightSimulatorPlugin(Entity):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.flights = {}
        self.simulators = {}

        # Listen
        self.is_listening = False
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.listen_socket.bind((settings.flightsim_recv_interface, settings.flightsim_recv_port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        # Send 
        self.is_sending = True
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.daemon = True
        self.send_thread.start()

    def listen(self):
        while True:
            if not self.is_listening:
                time.sleep(1.0)
                continue
            else:
                msg, address = self.listen_socket.recvfrom(1024)
                if (msg[:4]).decode('utf-8') == 'DATA': # X-Plane 12 
                    aircraft = XPlaneDecoder(msg, address)
                else: # FlightGear TODO: Make FlightGear header
                    aircraft = FlightGearDecoder(msg, address)

                self.flights[address] = aircraft

    def send(self):
        while True:
            if not self.is_sending:
                time.sleep(1.0)
                continue
            else:
                for address, aircraft in list(self.flights.items()):
                    aircraft: object[FlightSimAircraft]
                    callsign_own = aircraft.callsign
                    for callsign in traf.id:
                        idx = traf.id2idx(callsign)
                        actype = traf.type[idx]
                        latitude = traf.lat[idx]
                        longitude = traf.lon[idx]
                        airspeed = traf.tas[idx]
                        altitude = traf.alt[idx]
                        heading = traf.hdg[idx]
                        vertical_speed = traf.vs[idx]
                        if callsign != callsign_own: # Only send traffic without own aircraft
                            if aircraft.simname == 'FlightGear': 
                                packet = FlightGearPacket(callsign, actype, latitude, longitude, airspeed, altitude, phi=0.0, theta=0.0, psi=heading)
                                self.send_socket.sendto(packet, (address[0], settings.flightgear_multiplay_in_port))
  
    
    @core.timed_function(name='BLUESKY FLIGHTSIM-TRAFFIC UPDATE', dt=0.0)
    def update_bluesky_traffic(self):
        for address, aircraft in list(self.flights.items()):
            aircraft: object[FlightSimAircraft]
            self.simulators[address] = {'callsign': aircraft.callsign, 'sim': aircraft.simname, 'last_contact': aircraft.ts}

            idx = traf.id2idx(aircraft.callsign)
            if idx < 0:
                traf.cre(aircraft.callsign, aircraft.type, aircraft.latitude, aircraft.longitude, aircraft.psi, aircraft.altitude, aircraft.tas)
                stack.stack(f'ECHO New aircraft {aircraft.callsign} [{aircraft.type}] joined from {address} | {aircraft.simname}')
            else:
                traf.move(idx, aircraft.latitude, aircraft.longitude, aircraft.altitude, aircraft.psi, aircraft.tas, aircraft.vs)


    # --------- COMMANDS --------- #
    @stack.command(name='FLIGHTSIM', type='[onoff]', brief='FLIGHTSIM [ON/OFF]', help='Toggle [ON/OFF] FlightSim plugin')
    def toggle(self, flag):
        if flag:
            stack.stack(f'ECHO Listening for Flight Simulators on {settings.flightsim_recv_interface}:{settings.flightsim_recv_port}')
            self.is_listening = True
            self.is_sending = True
            stack.stack("OP")