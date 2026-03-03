"""
============================================================
| BlueSky plugin for FlightGear Flight Simulator v2024.1.4 |
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
from plugins.flightgear.src.core import Core

def init_plugin():
    """
    Initilisation of the BlueSky FlightGear Plugin.
    """
    version = json.load(open('./plugins/flightgear/version.json', 'r')).get('version')
    print(f"[BlueSky FlightGear plugin] : v{version} | Author: Max van Stuijvenberg")
    core = Core(version)
    config = {
        'plugin_name': 'flightgear',
        'plugin_type': 'sim',
        "update_interval": 0.0,
        "preupdate": core.update
    }

    stackfunctions = {
        "FLIGHTGEAR": [
            "FLIGHTGEAR [ON/OFF]",
            "[onoff]",
            core.toggle,
            "Start the FlightGear plugin"]
    }

    return config, stackfunctions

