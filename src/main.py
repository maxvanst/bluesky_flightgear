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
import numpy as np

# BlueSky imports
from bluesky import core, stack, settings, traf, sim
from bluesky.core import Entity

# Plugin imports
from .network.server import FlightGearMultiplayerServer

# Default Settings
settings.set_variable_defaults(flightgear_recv_interface='localhost', flightgear_recv_port=11002)

def init_plugin():
    plugin = FlightGearPlugin()
    config = {
        'plugin_name': 'FLIGHTGEAR',
        'plugin_type': 'sim'
    }
    return config

class FlightGearPlugin(Entity):
    def __init__(self):
        super().__init__()
        self.version = json.load(open('./plugins/bluesky_flightgear/version.json', 'r')).get('version')
        self.server = FlightGearMultiplayerServer(settings.flightgear_recv_interface, settings.flightgear_recv_port)

        with self.settrafarrays():
            self.is_flightgear = np.array([])
            self.squawk = np.array([])

    def create(self, n=1):
        super().create(n)
        self.is_flightgear[-n:] = False
        self.squawk[-n:] = 1200

    @core.timed_function(name='FLIGHTGEAR_TRAFFIC_UPDATER', dt=0.0)
    def update_traffic(self):
        for address, aircraft in list(self.server.listen_buffer.items()):
            aircraft: dict
            idx = traf.id2idx(aircraft.get('callsign'))
            if idx < 0:
                traf.cre(aircraft.get('callsign'), 
                         aircraft.get('type'), 
                         aircraft.get('latitude'), 
                         aircraft.get('longitude'), 
                         aircraft.get('true_heading'), 
                         aircraft.get('altitude'), 
                         aircraft.get('vtas'))
                self.is_flightgear[idx] = True
                stack.stack(f'ECHO FlightGear aircraft {aircraft.get('callsign')} [{aircraft.get('type')}] joined from [{address[0]}]')
            else:
                traf.move(idx, 
                          aircraft.get('latitude'), 
                          aircraft.get('longitude'), 
                          aircraft.get('altitude'), 
                          aircraft.get('true_heading'), 
                          aircraft.get('vtas'), 
                          aircraft.get('vs'))
                traf.perf.bank[idx] = aircraft.get('roll_angle') # Set roll angle

    @core.timed_function(name='FLIGHTGEAR_FLIGHTPLAN_UPDATER', dt=10.0)
    def update_flightplan(self):
        for address, aircraft in list(self.server.listen_buffer.items()):
            aircraft: dict
            callsign = aircraft.get('callsign')
            flightplan = self.server.get_flightplan(callsign)

            if len(flightplan) != 0 and len(flightplan[0]) == 4 and len(flightplan[-1]) == 4:
                stack.stack(f'DELRTE {callsign}')
                for wp in flightplan:
                    stack.stack(f"{callsign} ADDWPT {wp}")
            else:
                pass

    # ========================== BLUESKY COMMANDS ============================= #
    @stack.command(name='FLIGHTGEAR', type='[onoff]', brief='FLIGHTGEAR [ON/OFF]', help='Switch FlightGear plugin [ON/OFF]')
    def FLIGHTGEAR(self, flag):
        if flag:
            self.server.is_running = True
            stack.stack(f'ECHO FLIGHTGEAR PLUGIN v{self.version}')
            stack.stack(f'ECHO Listening for FlightGear simulators on [{settings.flightgear_recv_interface}:{settings.flightgear_recv_port}]')
            stack.stack('OP')

    @stack.command(name='FG_VERSION', brief='FG_VERSION', help='Show version of FlightGear plugin')
    def FG_VERSION(self):
        stack.stack(f'ECHO {self.version}')

    @stack.command(name='FG_SETTIME', brief='FG_GETHOST', help='Show host IP of a FlightGear aircraft')
    def FG_SETTIME(self, acid='acid', time=''):
        if self.is_flightgear[traf.id2idx(acid)]:
            self.server.set_time(acid, time)
        else:
            stack.stack(f'ECHO {acid} is not a FlightGear aircraft!')

    @stack.command(name='FG_GETHOST', brief='FG_GETHOST', help='Show host IP of a FlightGear aircraft')
    def FG_GETHOST(self, acid='acid'):
        if self.is_flightgear[traf.id2idx(acid)]:
            stack.stack(f'ECHO {acid} | HOST:{self.server.get_ipaddr_and_aircraft_of_callsign(acid)[0]}')
        else:
            stack.stack(f'ECHO {acid} is not a FlightGear aircraft!')

    @stack.command(name='FG_SENDCPDLC', brief='FG_CPDLC', help='Send a CPDLC message')
    def FG_SENDCPDLC(self, acid='acid', message=''):
        if self.is_flightgear[traf.id2idx(acid)]:
            self.server.send_cpdlc(acid, message)
        else:
            stack.stack(f'ECHO {acid} is not a FlightGear aircraft!')














    @stack.command(name='CPDLC')
    def CPDLC(self, acid, message):
        self.server.send_cpdlc(acid, message)