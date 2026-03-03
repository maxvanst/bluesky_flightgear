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
from plugins.flightsim.src.core import Core

def init_plugin():
    """
    Initilisation of the BlueSky FlightSim Plugin.
    """
    version = json.load(open('./plugins/flightsim/src/version.json', 'r')).get('version')
    print(f"[BlueSky FlightSim plugin] : v{version} | Author: Max van Stuijvenberg")
    core = Core(version)
    config = {
        'plugin_name': 'FLIGHTSIM',
        'plugin_type': 'sim',
        "update_interval": 0.0,
        "preupdate": core.update
    }

    stackfunctions = {
        "FLIGHTSIM": [
            "FLIGHTSIM [ON/OFF]",
            "[onoff]",
            core.toggle,
            "Start the FlightSim plugin"]
    }

    return config, stackfunctions

