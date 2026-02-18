import time
import socket
import threading
from bluesky import settings

class FlightGearConnect():
    def __init__(self):
        self.flights = {}
        self.is_connected = False
        self.buffer_size = 1024
        self.listener_thread = threading.Thread(target=self.listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((settings.flightgear_host, settings.flightgear_port))
            self.is_connected = True
            print(f"[FLIGHTGEAR] - Connected to {settings.flightgear_host}:{settings.flightgear_port}")

        except Exception as error:
            self.is_connected = False
            print(f"[FLIGHTGEAR] - {error}")

    def disconnect(self):
        try:
            self.sock.close()
            self.is_connected = False
            print("[FLIGHTGEAR] - Disconnected")

        except Exception as error:
            print(f"[FLIGHTGEAR] - {error}")

    def listener(self):
        while True:
            if not self.is_connected:
                time.sleep(1.0)
                continue
            else:
                data, address = self.sock.recvfrom(self.buffer_size)
                decoded = data.decode('utf-8').replace('"', '').split(";")
                flight = {'callsign': str(decoded[0]),
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
                        'destination': str(decoded[11])}
                
                self.flights[address] = flight