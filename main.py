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
from plugins.flightgear.network import Connection
from plugins.flightgear.traffic import Traffic
settings.set_variable_defaults(flightgear_host="127.0.0.1", flightgear_port=5501)

def init_plugin():
    """
    Initilisation of the BlueSky <---> FlightGear plugin
    """
    
    class FlightGear():
        def __init__(self):
            self.connection = Connection()
            self.traffic = Traffic()

        def toggle(self, flag):
            if flag:
                self.connection.connect()
            else:
                self.connection.disconnect()

        def update(self):
            if self.connection.is_connected:
                self.traffic.update(self.connection.buffer)

    flightgear = FlightGear()
    print("[FLIGHTGEAR] - FlightGear BlueSky plugin v0.0.0")
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
            "Start the FlightGear plugin"]
    }

    return config, stackfunctions