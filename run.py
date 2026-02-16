import time
import socket
import threading
import numpy as np

from bluesky import settings, stack, traf
from bluesky.tools import aero

from plugins.flightgear.aircraft import Aircraft

settings.set_variable_defaults(flightgear_host="127.0.0.1", flightgear_port=5501, flightgear_path="")

class FlightGear():
    def __init__(self):
        self.is_connected = False
        self.buffer_size = 1024
        self.receiver_thread = threading.Thread(target=self.receiver)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        self.acpool = {}
        self.aircraft = Aircraft()

    def toggle(self, flag=None):
        if flag is None:
            if self.is_connected:
                print(f"Listening on {settings.flightgear_host} on port {settings.flightgear_port}")
            else:
                print("Not connected")
        elif flag:
            self.connect()
        else:
            self.disconnect()

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock.bind((settings.flightgear_host, settings.flightgear_port))
            self.is_connected = True
            print(f"[FLIGHTGEAR] - Connected to {settings.flightgear_host}:{settings.flightgear_port}")

        except Exception as error:
            self.is_connected = False
            print(error)

    def disconnect(self):
        try:
            self.sock.close()
            for i, ac in list(self.acpool.items()):
                self.aircraft.delete(ac)
            self.is_connected = False
            print("[FLIGHTGEAR] - Disconnected")

        except Exception as error:
            print(error)

    def receiver(self):
        while True:
            if not self.is_connected:
                time.sleep(1.0)
                continue

            data, address = self.sock.recvfrom(self.buffer_size)
            decoded = data.decode('utf-8').replace('"', '').split(";")
            flight = {'address': str(address),
                    'callsign': str(decoded[0]),
                    'squawk': str(decoded[1]),
                    'actype': str(decoded[2]),
                    'ident': bool(int(decoded[3])),
                    'altitude': int(decoded[4]),
                    'airspeed': int(decoded[5]),
                    'vertical_speed': float(decoded[6]),
                    'heading': float(decoded[7]),
                    'latitude': float(decoded[8]),
                    'longitude': float(decoded[9]),
                    'origin': str(decoded[10]),
                    'destination': str(decoded[11]),
                    'route': str(decoded[12])}
            
            self.acpool[flight['callsign']] = flight
            print(flight["route"])

    def update(self):
        if self.is_connected:
            for i, ac in list(self.acpool.items()):
                if traf.id2idx(ac["callsign"]) < 0:
                    self.aircraft.create(ac)

                else:
                    self.aircraft.move(ac)

                    # Check if Aircraft is using IDENT
                    if ac["ident"]:
                        self.aircraft.ident(ac)
                    else:
                        self.aircraft.unident(ac)
                        
                    # FlightPlan
                    if ac["origin"] != "":
                        self.aircraft.flightplan_set_origin(ac)

                    if ac["destination"] != "":
                        self.aircraft.flightplan_set_destination(ac)