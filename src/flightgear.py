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
import json
import time
import socket
import struct
import numpy as np
import threading

from bluesky import core, stack, settings, traf, sim
from bluesky.core import Entity
from bluesky.tools import aero

settings.set_variable_defaults(flightgear_recv_interface='localhost', flightgear_recv_port=11002)

def init_plugin():
    version = json.load(open('./plugins/flightgear/version.json', 'r')).get('version')
    plugin = FlightGear(version)
    config = {
        'plugin_name': 'FLIGHTGEAR',
        'plugin_type': 'sim'
    }
    return config

class FlightGear(Entity):
    def __init__(self, version):
        super().__init__()
        self.version = version

        self.is_listening = False
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.listen_socket.bind((settings.flightgear_recv_interface, settings.flightgear_recv_port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def listen(self):
        while True:
            if not self.is_listening:
                time.sleep(1.0)
                continue
            else:
                msg, address = self.listen_socket.recvfrom(1024)
                header = (msg[:4]).decode('utf-8')
                if header == 'FGFS': # FlightGear
                    decoded = msg.decode('utf-8').replace('"', '').split(";")
                    print(decoded)
                    # aircraft = {'callsign': str(decoded[1]),
                    #             'squawk': str(decoded[2]),
                    #             'actype': str(decoded[3]),
                    #             'ident': bool(int(decoded[4])),
                    #             'altitude': int(decoded[5]),
                    #             'tas': int(decoded[6]),
                    #             'vs': float(decoded[7]),
                    #             'yaw': float(decoded[8]),
                    #             'latitude': float(decoded[9]),
                    #             'longitude': float(decoded[10])}
                    
                    # print(aircraft)
                else:
                    pass # Message was not from FlightGear so neglect

    # --------- COMMANDS --------- #
    @stack.command(name='FLIGHTGEAR', type='[onoff]', brief='FLIGHTGEAR [ON/OFF]', help='Toggle [ON/OFF] FlightGear plugin')
    def toggle(self, flag):
        if flag:
            self.is_listening = True
            stack.stack(f'ECHO Listening for FlightGear simulators on {settings.flightgear_recv_interface}:{settings.flightgear_recv_port}')