import time
import socket
import struct
import threading

from plugins.flightsim.src.flightgear.decode import decode as FlightGearDecoder
from plugins.flightsim.src.xplane.decode import decode as XPlaneDecoder

class FlightSimListener():
    def __init__(self):
        self.interface = '192.168.1.204'
        self.port = 10002
        self.is_listening = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.buffer = {}

    def start(self):
        self.is_listening = True
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

                self.buffer[address] = {'sim': aircraft.simname, 'aircraft': aircraft}