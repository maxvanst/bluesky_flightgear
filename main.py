"""
==========================================================
BlueSky plugin for FlightGear Flight Simulator v2024.1.4

M.J. van Stuijvenberg, 2026
-- Delft University of Technology (TU Delft)
-- Faculty of Aerospace Engineering

M.J.vanStuijvenberg@student.tudelft.nl

==========================================================
"""
import json
import time
import socket
import threading
from bluesky import settings, stack, traf, stack
from flightgear_python.fg_if import TelnetConnection
from plugins.flightgear.aircraft import Aircraft
settings.set_variable_defaults(bluesky_receive_udp_port=5501, flightgear_host="localhost", flightgear_telnet_port=5502)

def init_plugin():
    """
    Initilisation of the BlueSky FlightGear Plugin
    """
    
    author = "Max van Stuijvenberg"
    name = "BlueSky FlightGear Plugin"
    version = json.load(open('./plugins/flightgear/version.json', 'r')).get('version')
    flightgear = FlightGear(settings.bluesky_receive_udp_port, settings.flightgear_host, settings.flightgear_telnet_port)
    config = {
        'plugin_name': 'flightgear',
        'plugin_type': 'sim',
        "update_interval": 0.0,
        "preupdate": flightgear.update
    }

    stackfunctions = {
        "FLIGHTGEAR": [
            "FLIGHTGEAR [ON/OFF]",
            "[onoff]",
            flightgear.toggle,
            "Start the FlightGear plugin"]
    }
    print(f"[FLIGHTGEAR] - {name} | v{version} | Author: {author}")

    return config, stackfunctions


class FlightGear():
    def __init__(self, udp_port: int, flightgear_host: str, telnet_port: int):
        self.is_connected = False
        # UDP
        self.udp_is_connected = False
        self.udp_port = udp_port       
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.buffer = {}
        self.udp_listener_thread = threading.Thread(target=self.udp_listener)
        self.udp_listener_thread.daemon = True
        self.udp_listener_thread.start()
        # Telnet
        self.flightgear_host = flightgear_host 
        self.telnet_port = telnet_port          
        self.telnet_is_connected = False
        self.telnet = TelnetConnection(flightgear_host, telnet_port)

    def toggle(self, flag):
        if flag:
            self.connect()
            print(f"FLIGHTGEAR version:{self.get_flightgear_version()}")
            stack.stack("OP")
        else:
            print('plugin stopped')

    def connect(self):
        # UDP connection
        try:
            self.udp_socket.bind(("localhost", self.udp_port))
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_is_connected = True
        except Exception as error:
            print(error)

        # Telnet connection
        try:
            self.telnet.connect()
            self.telnet_is_connected = True
        except Exception as error:
            print(error)

        if self.udp_is_connected and self.telnet_is_connected:
            self.is_connected = True

    def udp_listener(self):
        while True:
            if not self.is_connected:
                time.sleep(1.0)
                continue
            else:
                data, address = self.udp_socket.recvfrom(1024)
                decoded = data.decode('utf-8').replace('"', '').split(";")
                callsign = str(decoded[0])
                flight = {'ts': time.time(),
                        'squawk': str(decoded[1]),
                        'actype': str(decoded[2]),
                        'ident': bool(int(decoded[3])),
                        'altitude': int(decoded[4]),
                        'airspeed': int(decoded[5]),
                        'vertical_speed': float(decoded[6]),
                        'heading': float(decoded[7]),
                        'latitude': float(decoded[8]),
                        'longitude': float(decoded[9])}
                
                self.buffer[callsign] = flight

    def update(self):
        for callsign, param in list(self.buffer.items()):
            aircraft = Aircraft(callsign, param)
            if traf.id2idx(callsign) < 0:
                aircraft.create()
                for wp in self.get_flightplan():
                    stack.stack(f"{callsign} ADDWPT {wp}")
            else:
                aircraft.move()
                
    def get_flightgear_version(self):
        return self.telnet.get_prop("/sim/version/flightgear")
    
    def get_udp_protocol_config(self):
        return self.telnet.get_prop("/io/channels/generic-1/config")
    
    def get_telnet_config(self):
        return self.telnet.get_prop("/io/channels/config")
    
    def get_flightplan(self):
        flightplan = []
        if self.telnet.get_prop("/autopilot/route-manager/active"):
            flightplan.append(self.telnet.get_prop("/autopilot/route-manager/departure/airport"))
            for id in range(1, self.telnet.get_prop("/autopilot/route-manager/route/num")-1):
                name = self.telnet.get_prop(f"/autopilot/route-manager/route/wp[{id}]/id")
                flightplan.append(name)
            flightplan.append(self.telnet.get_prop("/autopilot/route-manager/destination/airport"))

        return flightplan