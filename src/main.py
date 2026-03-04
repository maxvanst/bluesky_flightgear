"""
============================================================
|   BlueSky FlightSim plugin for FlightGear & X-Plane 12   |
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
import numpy as np

from bluesky.core import Entity
from bluesky import core, stack, traf
from bluesky.tools import aero

from plugins.flightsim.src.listener import FlightSimListener

def init_plugin():
    """
    Initilisation of the BlueSky FlightSim Plugin.
    """
    version = json.load(open('./plugins/flightsim/version.json', 'r')).get('version')
    plugin = FlightSim(version)
    config = {
        'plugin_name': 'FLIGHTSIM',
        'plugin_type': 'sim',
        'update_interval': 0.0,
        'preupdate': plugin.update
    }
    return config

class FlightSim(Entity):
    """
    FlightSim plugin Entity object for BlueSky
    """
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.clients = {}
        self.listener = FlightSimListener()

    @stack.command(name='FLIGHTSIM', type='[onoff]', brief='FLIGHTSIM [ON/OFF]', help='Toggle [ON/OFF] FlightSim plugin')
    def toggle(self, flag):
        if flag:
            print('Listening...')
            self.listener.start()

    @stack.command(name='FSSTATUS', brief='FLIGHTSIM STATUS', help='Show connected Flightsim Clients')
    def status(self):
        stack.stack(f'ECHO Connected clients: {self.clients}')

    def update(self):
        for address, param in list(self.listener.buffer.items()):
            callsign = 'PHLAB'
            idx = traf.id2idx(callsign)
            actype = str(param['actype'])
            latitude = float(param['latitude'])
            longitude = float(param['longitude'])
            heading = int(param['heading'])
            altitude = int(param["altitude"]) * aero.ft
            airspeed =  aero.tas2cas(int(param['airspeed']), altitude * aero.ft)
            vertical_speed = float(param['vertical_speed'])

            if traf.id2idx(callsign) < 0:
                traf.cre(callsign, actype, latitude, longitude, heading, altitude, airspeed)
            else:
                traf.move(idx, latitude, longitude, altitude, heading, airspeed, vertical_speed)