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
# General imports
import json
import time
import socket
import struct
import numpy as np
import threading
from scipy.spatial.transform import Rotation

# BlueSky imports
from bluesky import core, stack, settings, traf, sim
from bluesky.core import Entity
from bluesky.tools import aero

# Default Settings
settings.set_variable_defaults(flightgear_recv_interface='localhost', flightgear_recv_port=11002)

# BlueSky plugin initilisation
def init_plugin():
    version = json.load(open('./plugins/bluesky_flightgear/version.json', 'r')).get('version')
    plugin = FlightGearPlugin(version)
    config = {
        'plugin_name': 'FLIGHTGEAR',
        'plugin_type': 'sim'
    }
    return config

# FlightGear multiplayer protocol constants
MSG_MAGIC = 0x46474653      # "FGFS"
PROTO_VER = 0x00010001      # "1.1"
MAX_CHAT_MSG_LEN = 256
POS_DATA_ID = 0x00000007    # "7"

def create_message_header(callsign: str, msg_id: str, msg_len: int, requested_range_nm=100, reply_port=0):
    """
    Construct the Flightgear Multiplayer Protocol message header
    Source: https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py 

    Input:
        callsign:   str, callsign
        msg_id:     str, CHAT_MSG_ID or POS_DATA_ID
        msg_len:    int, length of message
    
    Returns:
        header:     bytes, header of FlightGear Multiplayer message
    """
    callsign_bytes = callsign.encode('ascii')[:8].ljust(8, b'\0')

    return struct.pack('!6I8s', MSG_MAGIC, PROTO_VER, msg_id, msg_len, requested_range_nm, reply_port, callsign_bytes)

def bluesky2ecef(alt: float, lat_deg: float, lon_deg: float, phi_deg: float, theta_deg: float, psi_deg: float):
    """
    FlightGear Multiplayer protocol uses ECEF (Earth-Centered, Earth-Fixed).
    This function converts Body reference frame => BlueSky geodetic reference frame => ECEF.

    Input:
        airspeed:   float, airspeed [m/s]
        alt:        float, altitude [m]
        lat_deg:    float, latitude [deg]
        lon_deg:    float, longitude [deg]
        phi_deg:    float, roll angle [deg]
        theta_deg:  float, pitch angle [deg]
        psi_deg     float, yaw angle [deg]

    Returns:
        position:    tuple, position vector within ECEF reference frame
        orientation: np.array, orientation vector within ECEF reference frame
    """
    # [deg] to [radians]
    lat, lon, phi, theta, psi = np.deg2rad(lat_deg), np.deg2rad(lon_deg), np.deg2rad(phi_deg), np.deg2rad(theta_deg), np.deg2rad(psi_deg)
    # ------------------ WGS84 ellipsoid parameters ------------------- #
    a = 6378137.0                                                       # Semi-major axis [m]
    b = 6356752.314245                                                  # Semi-minor axis [m]
    e = np.sqrt(1 - (b**2)/(a**2))                                      # Eccentricity    [-]
    Rm = (a * (1 - (e**2))) / ((1 - (e**2) * (np.sin(lat)**2))**(3/2))  # Meridian radius of curvature
    Rp = a / np.sqrt(1 - (e**2) * (np.sin(lat)**2))                     # Prime radius of curvature
                 
    # ----------- Position XYZ inside ECEF Reference Frame ------------ #
    PosX = (Rp + alt) * np.cos(lat) * np.cos(lon)                       # X coordinate ECEF [m]
    PosY = (Rp + alt) * np.cos(lat) * np.sin(lon)                       # Y coordinate ECEF [m]
    PosZ = ((b**2/a**2) * Rp + alt) * np.sin(lat)                       # Z coordinate ECEF [m]
    position = (PosX, PosY, PosZ)

    # ---------------- Reference Frame Transformations ---------------- #
    T_ecef2ned = Rotation.from_euler('yz', [-(90 + lat_deg), lon_deg], degrees=True).as_matrix()
    T_ned2body = Rotation.from_euler('xyz', [phi_deg, theta_deg, psi_deg], degrees=True).as_matrix()  

    rotation = T_ecef2ned @ T_ned2body

    orientation = Rotation.from_matrix(rotation).as_rotvec(degrees=False)

    return position, orientation

def create_packet(callsign: str, actype: str, latitude: float, longitude: float, airspeed: float, altitude: float, phi: float, theta: float, psi: float, chat_message: str):
    """
    Create Flightgear Multiplayer Protocol UDP Packet
    * Positions, Orientations, Velocities and Accelerations are w.r.t. the Earth-Centered, Earth-Fixed frame.
    Source 1: https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py  
    Source 2: https://wiki.flightgear.org/Multiplayer_protocol

    Input:
        callsign:   str, callsign
        actype:     str, actype
        latitude:   float, latitude [deg]
        longitude:  float, longitude [deg]
        airspeed:   float, airspeed [m/s]
        altitude:   float, altitude [m]
        phi:        float, roll angle [deg]
        theta:      float, pitch angle [deg]
        psi:        float, yaw angle [deg]

    Returns:
        packet
    """
    time_val = time.time()
    lag = 0
    linearVel, angularVel, linearAccel, angularAccel  = (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)
    position, orientation = bluesky2ecef(altitude, latitude, longitude, phi, theta, psi)
    model = ('AI/Aircraft/747/744-KLM}.xml').encode('ascii')[:96].ljust(96, b'\0')
    fmt = '!96s2d3d3f3f3f3f3f'
    payload = struct.pack(fmt, model, time_val, lag, *position, *orientation, *linearVel, *angularVel, *linearAccel, *angularAccel)

    protocol_version = struct.pack('!h', 10) + struct.pack('!h', 2)
    squawk = struct.pack('!h', 1500) + struct.pack('!h', 1200)

    transponder_altitude = struct.pack('!h', 1501) + struct.pack('!h', int(altitude / aero.ft))
    transponder_mode = struct.pack('!h', 1503) + struct.pack('!h', 2) # set to TA/RA so TCAS works
    transponder_airspeed = struct.pack('!h', 1505) + struct.pack('!h', int(airspeed / aero.kts))

    chat = struct.pack('!HH', 10002, len(chat_message)) + chat_message.encode('utf-8')

                             # 4 bytes       
    pos_msg = payload + b'\x1f\xac\xe0\x02' + protocol_version 
    pos_msg += squawk + transponder_altitude + transponder_mode + transponder_airspeed + chat

    if len(pos_msg) % 4 != 0:
        pos_msg += b'\0' * (4 - (len(pos_msg) % 4))

    msg_len = 32 + len(pos_msg)
    header = create_message_header(callsign, POS_DATA_ID, msg_len)
    packet = header + pos_msg

    return packet

class FlightGearPlugin(Entity):
    def __init__(self, version):
        super().__init__()
        self.is_running = False
        self.version = version
        self.clients = {}

        # Listen
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.listen_socket.bind((settings.flightgear_recv_interface, settings.flightgear_recv_port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.listen_buffer = {}

        # Send 
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.daemon = True
        self.send_thread.start()

        with self.settrafarrays():
            self.is_flightgear = np.array([])
            self.squawk = np.array([])

    def create(self, n=1):
        super().create(n)
        self.is_flightgear[-n:] = False
        self.squawk[-n:] = 1200

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
                    # TODO: Dynamic XML reading based on bluesky.xml
                    simulator = {
                        'last_contact': time.strftime('%H:%M:%S'),      # [-]
                        'name': str(decoded[1]),                        # [-]
                        'ip': str(decoded[2]),                          # [-]
                        'tfc_recv_port': str(decoded[3]),               # [-]
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
                        'vertical_speed': float(decoded[15]) * aero.ft, # [m/s]
                        'angle_of_attack': float(decoded[16]),          # [deg]
                        'sideslip_angle': float(decoded[17]),           # [deg]
                        'path_angle': float(decoded[18]),               # [deg]
                        'pitch_angle': float(decoded[19]),              # [deg]
                        'roll_angle': float(decoded[20]),               # [deg]
                        'yaw_angle': float(decoded[21]),                # [deg]
                        'true_heading': float(decoded[22]),             # [deg]
                    }
                    self.listen_buffer[address] = simulator
                    self.clients[address] = {'last_contact': simulator.get('last_contact')}
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
                            self.send_socket.sendto(packet, (address[0], 5002))

    def get_ipaddr_of_callsign(self, callsign):
        for address, aircraft in list(self.listen_buffer.items()):
            aircraft: dict
            if aircraft.get('callsign') == callsign:
                return address[0]

    @core.timed_function(dt=0.0)
    def update(self):
        for address, aircraft in list(self.listen_buffer.items()):
            aircraft: dict
            idx = traf.id2idx(aircraft.get('callsign'))
            if idx < 0:
                traf.cre(aircraft.get('callsign'), 
                         aircraft.get('type'), 
                         aircraft.get('latitude'), 
                         aircraft.get('longitude'), 
                         aircraft.get('true_heading'), 
                         aircraft.get('altitude'), 
                         aircraft.get('vtas'))
                
                self.is_flightgear[idx] = True
                stack.stack(f'ECHO New FlightGear aircraft {aircraft.get('callsign')} [{aircraft.get('type')}] joined from {address[0]}')
            else:
                traf.move(idx, 
                          aircraft.get('latitude'), 
                          aircraft.get('longitude'), 
                          aircraft.get('altitude'), 
                          aircraft.get('true_heading'), 
                          aircraft.get('vtas'), 
                          aircraft.get('vs'))
                traf.perf.bank[idx] = aircraft.get('roll_angle') # Set roll angle

    # --------- COMMANDS --------- #
    #TODO: @stack.commandgroup(name='FLIGHTGEAR')???
    @stack.command(name='FLIGHTGEAR', type='[onoff]', brief='FLIGHTGEAR [ON/OFF]', help='Toggle [ON/OFF] FlightGear plugin')
    def FLIGHTGEAR(self, flag):
        if flag == 'ON':
            self.is_running = True
            stack.stack(f'ECHO FLIGHTGEAR PLUGIN v{self.version}')
            stack.stack(f'ECHO Listening for FlightGear simulators on {settings.flightgear_recv_interface}:{settings.flightgear_recv_port}')
            stack.stack('OP')
    
    @stack.command(name='FGLIST', help='Show connected FlightGear simulators')
    def FGLIST(self):
        stack.stack(f'ECHO {self.clients}')

    @stack.command(name='FGSHOW', type='[onoff]', brief='FGSHOW [ON/OFF]', help='Toggle showing FlightGear aircraft on Radar [ON/OFF]')
    def FGSHOW(self, flag):
        for id in traf.id:
            idx = traf.id2idx(id)
            if self.is_flightgear[idx]:
                if flag == 'ON':
                    stack.stack(f'COLOR {id} 0,0,255')
                else:
                    stack.stack(f'COLOR {id} 0,255,0')

    @stack.command(name='SETSQUAWK')
    def SETSQUAWK(self, acid):
        self.squawk[acid] = 2200 