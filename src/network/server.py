# General imports
import time
import socket
import threading
import numpy as np

# BlueSky imports
from bluesky import traf
from bluesky.tools import aero

# Plugin imports
from .protocol import create_packet

class FlightGearMultiplayerServer():
    def __init__(self, flightgear_recv_interface: str, flightgear_recv_port: int):
        self.is_running = False
        self.connected_clients = {}

        # Listen
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.listen_socket.bind((flightgear_recv_interface, flightgear_recv_port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.listen_buffer = {}

        # Send 
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.daemon = True
        self.send_thread.start()

    def listen(self):
        while True:
            if not self.is_running:
                time.sleep(1.0)
                continue
            else:
                msg, address = self.listen_socket.recvfrom(1024)
                header = (msg[:4]).decode('utf-8')
                if header == 'FGFS': # FlightGear
                    decoded = msg.decode('utf-8').replace('"', '').split(";")
                    # TODO: Dynamic XML reading based on bluesky.xml / or implement FlightGear multiplayer protocol
                    simulator = {
                        'last_contact': time.strftime('%H:%M:%S'),      # [-]
                        'name': str(decoded[1]),                        # [-]
                        'ip': str(decoded[2]),                          # [-]
                        'tfc_recv_port': int(decoded[3]),               # [-]
                        'telnet_port': str(decoded[4]),                 # [-]
                        'callsign': str(decoded[5]),                    # [-]
                        'type': str(decoded[6]),                        # [-]
                        'squawk': int(decoded[7]),                      # [-]
                        'transponder_mode': int(decoded[8]),            # [-]
                        'transponder_ident': bool(int(decoded[9])),     # [-]
                        'latitude': float(decoded[10]),                 # [deg]
                        'longitude': float(decoded[11]),                # [deg]
                        'altitude': float(decoded[12]) * aero.ft,       # [m]
                        'altitude_agl': float(decoded[13]) * aero.ft,   # [m]
                        'vtas': float(decoded[14]) * aero.kts,          # [m/s]
                        'vs': float(decoded[15]) * aero.ft,             # [ft/min]
                        'angle_of_attack': float(decoded[16]),          # [deg]
                        'sideslip_angle': float(decoded[17]),           # [deg]
                        'path_angle': float(decoded[18]),               # [deg]
                        'pitch_angle': float(decoded[19]),              # [deg]
                        'roll_angle': float(decoded[20]),               # [deg]
                        'yaw_angle': float(decoded[21]),                # [deg]
                        'true_heading': float(decoded[22]),             # [deg]
                    }
                    self.listen_buffer[address] = simulator
                    self.connected_clients[address] = {'last_contact': simulator.get('last_contact')}
                else:
                    pass # Message was not from FlightGear so neglect message
    
    def send(self):
        while True:
            if not self.is_running:
                time.sleep(1.0)
                continue
            else:
                for address, aircraft in list(self.listen_buffer.items()):
                    aircraft: dict
                    callsign_own = aircraft.get('callsign')
                    for callsign in traf.id:
                        if callsign != callsign_own: # Only send traffic without own aircraft
                            idx = traf.id2idx(callsign)
                            actype = traf.type[idx]
                            latitude = traf.lat[idx]
                            longitude = traf.lon[idx]
                            airspeed = traf.tas[idx]
                            altitude = traf.alt[idx]
                            heading = traf.hdg[idx]
                            bank = np.rad2deg(traf.perf.bank[idx])
                            vertical_speed = traf.vs[idx]
                            gamma = 0
                            if airspeed != 0:
                                gamma = np.rad2deg(np.asin(vertical_speed / airspeed))
                                
                            packet = create_packet(callsign, actype, latitude, longitude, airspeed, altitude, phi=bank, theta=gamma, psi=heading, chat_message='JOINED FROM BLUESKY')
                            self.send_socket.sendto(packet, (address[0], aircraft.get('tfc_recv_port')))