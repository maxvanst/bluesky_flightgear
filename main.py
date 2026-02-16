"""
==========================================================
BlueSky plugin for FlightGear Flight Simulator v2024.1.4

M.J. van Stuijvenberg, 2026
-- Delft University of Technology (TU Delft)
-- Faculty of Aerospace Engineering

M.J.vanStuijvenberg@student.tudelft.nl

==========================================================
"""
from bluesky import settings
from plugins.flightgear.run import FlightGear

def init_plugin():
    """
    Initilisation of the BlueSky <---> FlightGear plugin
    """
    print("[FLIGHTGEAR] - FlightGear BlueSky plugin v0.0.0")

    flightgear = FlightGear()
    config = {
        'plugin_name': 'flightgear',
        'plugin_type': 'sim',
        "update_interval": 0.0,
        "preupdate": flightgear.update,
    }

    stackfunctions = {
        "FLIGHTGEAR": [
            "FLIGHTGEAR [ON/OFF]",
            "[onoff]",
            flightgear.toggle,
            "Start the FlightGear plugin"],
    }

    return config, stackfunctions

