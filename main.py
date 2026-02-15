"""
==========================================================
BlueSky plugin for FlightGear Flight Simulator v2024.1.4

M.J. van Stuijvenberg, 2026
-- Delft University of Technology (TU Delft)
-- Faculty of Aerospace Engineering

M.J.vanStuijvenberg@student.tudelft.nl

==========================================================
"""
# Copied and made small changes to TcpSocket /bluesky/tools/network.py
# Copied aircraft loading and commands from /bluesky/plugins/adsbfeed.py

import numpy as np
from bluesky import core, settings, stack, traf
from bluesky.tools import aero
from plugins.flightgear.network import FG_UDP_Listener

def init_plugin():
    """
    Initilisation of the BlueSky plugin
    """
    flightgear = FG_UDP_Listener()
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
            "Start a FlightGear connection"]
    }

    return config, stackfunctions
