import time
import socket
import struct
import threading

from bluesky import settings

from plugins.flightsim.src.flightgear.decode import decode as FlightGearDecoder
from plugins.flightsim.src.xplane.decode import decode as XPlaneDecoder

class FlightSimListener():
    def __init__(self):
        self.interface = settings.flightsim_interface
        self.port = settings.flightsim_recv_port
        self.is_listening = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.buffer = {}

    def start(self):
        self.is_listening = True
        print(f'Listening on {self.interface}:{self.port}')
        self.socket.bind((self.interface, self.port))
        self.thread.start()

    def listen(self):
        while True:
            if not self.is_listening:
                time.sleep(1.0)
                continue
            else:
                msg, address = self.socket.recvfrom(1024)
                if (msg[:4]).decode('utf-8') == 'DATA': 
                    # ----------------------- X-Plane 12 ------------------------- #
                    aircraft = XPlaneDecoder(msg, address)
                else: 
                    # ----------------------- FlightGear ------------------------- #
                    aircraft = FlightGearDecoder(msg, address)

                self.buffer[address] = aircraft