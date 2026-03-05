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
from plugins.flightsim.src.sender import FlightSimSender
from plugins.flightsim.src.aircraft import FlightSimAircraft

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
        self.sender = FlightSimSender()

    @stack.command(name='FLIGHTSIM', type='[onoff]', brief='FLIGHTSIM [ON/OFF]', help='Toggle [ON/OFF] FlightSim plugin')
    def toggle(self, flag):
        if flag:
            self.listener.start()
            self.sender.start()
            stack.stack("OP")
            
    @stack.command(name='FSSTATUS', brief='FLIGHTSIM STATUS', help='Show connected Flightsim Clients')
    def status(self):
        stack.stack(f'ECHO Connected clients: {self.clients}')

    def update(self):
        for address, aircraft in list(self.listener.buffer.items()):
            aircraft: object[FlightSimAircraft]
            idx = traf.id2idx(aircraft.callsign)
            if idx < 0:
                traf.cre(aircraft.callsign, aircraft.type, aircraft.latitude, aircraft.longitude, aircraft.psi, aircraft.altitude, aircraft.tas)
            else:
                traf.move(idx, aircraft.latitude, aircraft.longitude, aircraft.altitude, aircraft.psi, aircraft.tas, aircraft.vs)