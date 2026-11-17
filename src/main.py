# src/main.py

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

# BlueSky imports
from bluesky import stack, settings
from bluesky.core import Entity

# Import pyproject.toml and plugin version
import tomllib
from pathlib import Path

pyproject = Path(__file__).parents[1] / "pyproject.toml"

with pyproject.open("rb") as f:
    config = tomllib.load(f)

# Plugin imports
from .multiplayer.server import FlightGearMultiplayerServer

# Default Settings
settings.set_variable_defaults(flightgear_recv_interface='localhost', flightgear_recv_port=5000)

def init_plugin():
    """Plugin initialisation - required by BlueSky plugin API"""
    plugin = FlightGearPlugin()
    config = {
        'plugin_name': 'FLIGHTGEAR',
        'plugin_type': 'sim'
    }
    return config

class FlightGearPlugin(Entity):
    """Main Flightgear plugin entry point to the BlueSky simulation."""
    def __init__(self):
        super().__init__()
        # Project version
        self.version = config["project"]["version"]

        # Setup of interface and ports for FlightGear Multiplayer Server e.g. localhost v.s. 0.0.0.0 and port 1-65535
        self.server = FlightGearMultiplayerServer(
            receive_interface=settings.flightgear_recv_interface,
            receive_port=settings.flightgear_recv_port
            )

    @stack.command(name="FLIGHTGEAR", brief="FLIGHTGEAR [ON/OFF/VERSION/HELP]", help="Control the FlightGear interface")
    def FLIGHTGEAR(self, flag: str) -> None:
        """The function defines the commands available inside the BlueSky to simulation that allow interaction with the plugin."""
        if flag == "ON":
            self.server._listener = True
        elif flag == "OFF":
            self.server._listener  = False
        elif flag == "HELP":
            stack.stack(f"ECHO ON: START PLUGIN - OFF: STOP PLUGIN")
        else:
            stack.stack(f"ECHO {flag} is not recognized as an FlightGear plugin command!")