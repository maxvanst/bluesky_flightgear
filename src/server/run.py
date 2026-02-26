import socket
import time
import threading
from bluesky import traf
from plugins.flightgear.src.server.protocol import create_packet

class Server():
    """
    FlightGear Multiplayer Server with connections to BlueSky
    * Inbound UDP protocol called ./protocol/bluesky.xml
    * Outbound UDP protocol is the FlightGear Multiplayer Protocol
    """
    def __init__(self):
        self.is_listening = False
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_buffer = {}
        # ------------------------- #
        self.is_sending = False
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.daemon = True

    def start(self):
        self.is_listening = True
        self.listen_socket.bind(("localhost", 5000))
        self.listen_thread.start()
        # ------------------------- #
        self.is_sending = True
        self.send_thread.start()

    def listen(self):
        """
        Listen thread function for UDP packets coming from FlightGear using the ./protocol/bluesky.xml protocol.
        If a packet is received it is stored in a buffer with as key the callsign.
        """
        while True:
            if not self.is_listening:
                time.sleep(1.0)
                continue
            else:
                data, address = self.listen_socket.recvfrom(1024)
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
                
                self.listen_buffer[callsign] = flight

    def send(self):
        """
        Send thread function that sends BlueSky Traffic + Incoming FlightGear traffic to all connected clients. 
        This is done using the FlightGear Multiplayer protocol.
        """
        while True:
            if not self.is_sending:
                time.sleep(1.0)
                continue
            else:
                for callsign in traf.id:
                    idx = traf.id2idx(callsign)
                    actype = traf.type[idx]
                    latitude = traf.lat[idx]
                    longitude = traf.lon[idx]
                    altitude = traf.alt[idx]
                    heading = traf.hdg[idx]
                    vertical_speed = traf.vs[idx]
                    accel_x = traf.ax[idx]
                    packet = create_packet(callsign, actype, latitude, longitude, altitude, phi=0.0, theta=0.0, psi=heading)
                    self.send_socket.sendto(packet, ("127.0.0.1", 5002))    