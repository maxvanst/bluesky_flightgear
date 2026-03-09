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

    @core.timed_function(name='FLIGHTGEAR_TRAFFIC_UPDATER', dt=1.0)
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
                stack.stack(f'ECHO FlightGear aircraft {aircraft.get('callsign')} [{aircraft.get('type')}] joined from {address[0]}')
            else:
                traf.move(idx, 
                          aircraft.get('latitude'), 
                          aircraft.get('longitude'), 
                          aircraft.get('altitude'), 
                          aircraft.get('true_heading'), 
                          aircraft.get('vtas'), 
                          aircraft.get('vs'))
                traf.perf.bank[idx] = aircraft.get('roll_angle') # Set roll angle

    @core.timed_function(name='FLIGHTGEAR_FLIGHTPLAN_UPDATER', dt=5.0)
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
            
    @stack.commandgroup(name='FLIGHTGEAR')
    def FLIGHTGEAR(self, function: str, *args):
        if function == 'ON':
            self.server.is_running = True
            stack.stack(f'ECHO FLIGHTGEAR PLUGIN v{self.version}')
            stack.stack(f'ECHO Listening for FlightGear simulators on {settings.flightgear_recv_interface}:{settings.flightgear_recv_port}')
            stack.stack('OP')

        if function == 'LIST':
            stack.stack(f'ECHO {self.version}')

    @stack.command(name='CPDLC')
    def CPDLC(self, acid, message):
        self.server.send_cpdlc(acid, message)