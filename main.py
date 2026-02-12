"""
==========================================================
BlueSky plugin for FlightGear Flight Simulator v2024.1.4

M.J. van Stuijvenberg, 2026
-- Delft University of Technology (TU Delft)
-- Faculty of Aerospace Engineering

M.J.vanStuijvenberg@student.tudelft.nl

==========================================================
"""
# Copied and made small changes to TcpSocket ./tools/network.py
# Copied aircraft loading and commands from ./plugins/adsbfeed.py

import time
from bluesky import settings, stack, traf
from plugins.flightgear.network import UDPSocket
from bluesky.tools import aero

settings.set_variable_defaults(flightgear_host="127.0.0.1", flightgear_port=5501)

def init_plugin():
    """
    Initilisation of the BlueSky plugin
    """

    sim = FlightGear()
    config = {
        'plugin_name': 'flightgear',
        'plugin_type': 'sim',
        "update_interval": 0.0,
        "preupdate": sim.update,
    }

    stackfunctions = {
        "FLIGHTGEAR": [
            "FLIGHTGEAR [ON/OFF]",
            "[onoff]",
            sim.toggle,
            "Start a FlightGear connection",
        ]
    }

    return config, stackfunctions

class FlightGear(UDPSocket):
    def __init__(self):
        super().__init__()
        self.acpool = {}

    def processData(self, data, address):
        decoded = data.decode('utf-8').replace('"', '').split(";")
        flight = {'address': address,
                'callsign': 'PH-LAB',
                'squawk': decoded[0],
                'actype': decoded[1],
                'ident': decoded[2],
                'altitude': decoded[3],
                'airspeed': decoded[4],
                'vertical_speed': decoded[5],
                'heading': decoded[6],
                'latitude': decoded[7],
                'longitude': decoded[8],
                'origin': decoded[9],
                'destination': decoded[10]}
                
        self.acpool[flight['callsign']] = flight

    def update(self):
        if self.isConnected():
            params = ("latitude", "longitude", "altitude", "airspeed", "heading", "callsign", "vertical_speed", "actype")
            for i, d in list(self.acpool.items()):
                if set(params).issubset(d):
                    acid = d["callsign"]
                    if traf.id2idx(acid) < 0:
                        # Create aircraft
                        cmdstr = "CRE %s, %s, %f, %f, %f, %d, %f" % (
                            acid,
                            str(d["actype"]),
                            float(d["latitude"]),
                            float(d["longitude"]),
                            float(d["heading"]),
                            int(d["altitude"]),
                            0.0
                        )
                        stack.stack(cmdstr)

                    else:
                        # Update aircraft
                        cmdstr = "MOVE %s, %f, %f, %d, %f, %f, %f" % (
                            acid,
                            float(d["latitude"]),
                            float(d["longitude"]),
                            int(d["altitude"]),
                            float(d["heading"]),
                            aero.tas2cas(int(d["airspeed"]), int(d["altitude"]) * aero.ft),
                            float(d["vertical_speed"])
                        )
                        stack.stack(cmdstr)
        return 

    def toggle(self, flag=None):
        if flag is None:
            if self.isConnected():
                print(f"Connected to {settings.flightgear_host} on port {settings.flightgear_port}")
            else:
                print("Not connected")
        elif flag:
            self.connectToHost(settings.flightgear_host, settings.flightgear_port)
        else:
            self.disconnectFromHost()