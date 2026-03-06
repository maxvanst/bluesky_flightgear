"""
============================================================
|                BlueSky FlightGear plugin                 |
|                                                          | 
|               M.J. van Stuijvenberg, 2026                |
|        Delft University of Technology (TU Delft)         |
|            Faculty of Aerospace Engineering              |
|                                                          |
|          M.J.vanStuijvenberg@student.tudelft.nl          |
============================================================
"""
# General imports
import json
import time
import socket
import struct
import numpy as np
import threading

# BlueSky imports
from bluesky import core, stack, settings, traf, sim
from bluesky.core import Entity
from bluesky.tools import aero

# Own plugin imports
from plugins.bluesky_flightgear.src.server.protocol import create_packet, create_message_packet

# Default Settings
settings.set_variable_defaults(flightgear_recv_interface='localhost', flightgear_recv_port=11002)

def init_plugin():
    version = json.load(open('./plugins/bluesky_flightgear/version.json', 'r')).get('version')
    plugin = FlightGearPlugin(version)
    config = {
        'plugin_name': 'FLIGHTGEAR',
        'plugin_type': 'sim'
    }
    return config

class FlightGearPlugin(Entity):
    def __init__(self, version):
        super().__init__()
        self.is_running = False
        self.version = version
        self.clients = {}

        # Listen
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.listen_socket.bind((settings.flightgear_recv_interface, settings.flightgear_recv_port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.listen_buffer = {}

        # Send 
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.daemon = True
        self.send_thread.start()

        with self.settrafarrays():
            self.is_flightgear = np.array([])
            self.squawk = np.array([])

    def create(self, n=1):
        super().create(n)
        self.is_flightgear[-n:] = False

    def listen(self):
        while True:
            if not self.is_running:
                time.sleep(1.0)
                continue
            else:
                msg, address = self.listen_socket.recvfrom(1024)
                header = (msg[:4]).decode('utf-8')
                if header == 'FGFS': # FlightGear
                    decoded = msg.decode('utf-8').replace('"', '').split(";")
                    # TODO: Dynamic XML reading based on bluesky.xml
                    simulator = {
                        'last_contact': time.strftime('%H:%M:%S'),      # [-]
                        'sim_name': str(decoded[1]),                    # [-]
                        'sim_ip': str(decoded[2]),                      # [-]
                        'sim_tfc_recv_port': str(decoded[3]),           # [-]
                        'sim_telnet_port': str(decoded[4]),             # [-]
                        'callsign': str(decoded[5]),                    # [-]
                        'type': str(decoded[6]),                        # [-]
                        'squawk': int(decoded[7]),                      # [-]
                        'transponder_mode': int(decoded[8]),            # [-]
                        'transponder_ident': bool(int(decoded[9])),     # [-]
                        'latitude': float(decoded[10]),                 # [deg]
                        'longitude': float(decoded[11]),                # [deg]
                        'altitude': float(decoded[12]) * aero.ft,       # [m]
                        'altitude_agl': float(decoded[13]) * aero.ft,   # [m]
                        'vtas': float(decoded[14]) * aero.kts,          # [m/s]
                        'vertical_speed': float(decoded[15]) * aero.ft, # [m/s]
                        'angle_of_attack': float(decoded[16]),          # [deg]
                        'sideslip_angle': float(decoded[17]),           # [deg]
                        'path_angle': float(decoded[18]),               # [deg]
                        'pitch_angle': float(decoded[19]),              # [deg]
                        'roll_angle': float(decoded[20]),               # [deg]
                        'yaw_angle': float(decoded[21]),                # [deg]
                        'true_heading': float(decoded[22]),             # [deg]
                    }
                    self.listen_buffer[address] = simulator
                    self.clients[address] = {'last_contact': simulator.get('last_contact')}
                else:
                    pass # Message was not from FlightGear so neglect message

    def send(self):
        while True:
            if not self.is_running:
                time.sleep(1.0)
                continue
            else:
                for address, aircraft in list(self.listen_buffer.items()):
                    aircraft: dict
                    callsign_own = aircraft.get('callsign')
                    for callsign in traf.id:
                        idx = traf.id2idx(callsign)
                        actype = traf.type[idx]
                        latitude = traf.lat[idx]
                        longitude = traf.lon[idx]
                        airspeed = traf.tas[idx]
                        altitude = traf.alt[idx]
                        heading = traf.hdg[idx]
                        vertical_speed = traf.vs[idx]
                        gamma = 0
                        if airspeed != 0:
                            gamma = np.rad2deg(np.asin(vertical_speed / airspeed))

                        if callsign != callsign_own: # Only send traffic without own aircraft
                            packet = create_packet(callsign, actype, latitude, longitude, airspeed, altitude, phi=0.0, theta=-gamma, psi=heading)
                            self.send_socket.sendto(packet, (address[0], 5002))

    def get_ipaddr_of_callsign(self, callsign):
        for address, aircraft in list(self.listen_buffer.items()):
            aircraft: dict
            if aircraft.get('callsign') == callsign:
                return address[0]

    @core.timed_function(dt=0.0)
    def update(self):
        for address, aircraft in list(self.listen_buffer.items()):
            aircraft: dict
            idx = traf.id2idx(aircraft.get('callsign'))
            if idx < 0:
                traf.cre(aircraft.get('callsign'), 
                         aircraft.get('type'), 
                         aircraft.get('latitude'), 
                         aircraft.get('longitude'), 
                         aircraft.get('psi'), 
                         aircraft.get('altitude'), 
                         aircraft.get('vtas'))
                
                self.is_flightgear[idx] = True
                stack.stack(f'ECHO New FlightGear aircraft {aircraft.get('callsign')} [{aircraft.get('type')}] joined from {address[0]}')
            else:
                traf.move(idx, 
                          aircraft.get('latitude'), 
                          aircraft.get('longitude'), 
                          aircraft.get('altitude'), 
                          aircraft.get('psi'), 
                          aircraft.get('vtas'), 
                          aircraft.get('vs'))

    # --------- COMMANDS --------- #
    #TODO: @stack.commandgroup(name='FLIGHTGEAR')???
    @stack.command(name='FLIGHTGEAR', type='[onoff]', brief='FLIGHTGEAR [ON/OFF]', help='Toggle [ON/OFF] FlightGear plugin')
    def FLIGHTGEAR(self, flag):
        if flag == 'ON':
            self.is_running = True
            stack.stack(f'ECHO Listening for FlightGear simulators on {settings.flightgear_recv_interface}:{settings.flightgear_recv_port}')
            stack.stack('OP')
    
    @stack.command(name='FGLIST')
    def FGLIST(self):
        stack.stack(f'ECHO {self.clients}')

    @stack.command(name='FGSHOW', type='[onoff]', brief='FGSHOW [ON/OFF]', help='Toggle showing FlightGear aircraft on Radar [ON/OFF]')
    def FGSHOW(self, flag):
        for id in traf.id:
            idx = traf.id2idx(id)
            if self.is_flightgear[idx]:
                if flag == 'ON':
                    stack.stack(f'COLOR {id} 0,0,255')
                else:
                    stack.stack(f'COLOR {id} 0,255,0')