import struct
import math
import time
import numpy as np
from bluesky.tools import aero
from math import sqrt, radians, sin, cos, acos, pi
from scipy.spatial.transform import Rotation

from plugins.bluesky_flightgear.src.server.mapping import model_mapping

# FlightGear multiplayer protocol constants
MSG_MAGIC = 0x46474653      # "FGFS"
PROTO_VER = 0x00010001      # "1.1"
CHAT_MSG_ID = 0x00000001    # "1"
MAX_CHAT_MSG_LEN = 256
POS_DATA_ID = 0x00000007    # "7"

def bluesky2ecef(alt: float, lat_deg: float, lon_deg: float, phi_deg: float, theta_deg: float, psi_deg: float):
    """
    FlightGear Multiplayer protocol uses ECEF (Earth-Centered, Earth-Fixed).
    This function converts BlueSky geodetic reference frame to ECEF.
    * Positions are in with respect to the Earth centered frame.
    * Orientations are with respect to the X, Y and Z axis of the Earth centered frame
      ,stored in the angle axis representation where the angle is coded into the axis length.

    Source 1: Navigation Equations Module 2 Lecture Slides AE4302 (Avionics and Operations)
    Source 2: Navigation Equations Module 4 Lecture Slides AE4302 (Avionics and Operations)
    Source 3: https://en.wikipedia.org/wiki/Geographic_coordinate_conversion

    Input:
        airspeed:   float, airspeed [m/s]
        alt:        float, altitude [m]
        lat_deg:    float, latitude [deg]
        lon_deg:    float, longitude [deg]
        phi_deg:    float, roll angle [deg]
        theta_deg:  float, pitch angle [deg]
        psi_deg     float, yaw angle [deg]

    Returns:
        (PosX, PosY, PosZ): tuple, position vector within ECEF reference frame
        (orientation):      np.array, orientation vector within ECEF reference frame
    """
    # [deg] to [radians]
    lat, lon, phi, theta, psi = radians(lat_deg), radians(lon_deg), radians(phi_deg), radians(theta_deg), radians(psi_deg)
    # ------------------ WGS84 ellipsoid parameters ------------------- #
    a = 6378137.0                                                       # Semi-major axis [m]
    b = 6356752.314245                                                  # Semi-minor axis [m]
    e = sqrt(1 - (b**2)/(a**2))                                         # Eccentricity    [-]
    Rm = (a * (1 - (e**2))) / ((1 - (e**2) * (sin(lat)**2))**(3/2))     # Meridian radius of curvature
    Rp = a / sqrt(1 - (e**2) * (sin(lat)**2))                           # Prime radius of curvature
                                                                    
    # ----------- Position XYZ inside ECEF Reference Frame ------------ #
    PosX = (Rp + alt) * cos(lat) * cos(lon)                             # X coordinate ECEF [m]
    PosY = (Rp + alt) * cos(lat) * sin(lon)                             # Y coordinate ECEF [m]
    PosZ = ((b**2/a**2) * Rp + alt) * sin(lat)                          # Z coordinate ECEF [m]
    
    # ---------------- Reference Frame Transformations ---------------- #
    T_enu2ecef = np.array([[-sin(lon), -sin(lat)*cos(lon), cos(lat)*cos(lon)],  # E
                           [cos(lon) , -sin(lat)*sin(lon), cos(lat)*sin(lon)],  # N
                           [0        , cos(lat)          , sin(lat)         ]]) # U

    rot = T_enu2ecef @ np.array([[cos(-psi + pi/2), -sin(-psi + pi/2), 0],
                                 [sin(-psi + pi/2),  cos(-psi + pi/2), 0],
                                 [0, 0, 1]])
    
    rot = rot @ np.array([[cos(theta) , 0, sin(theta)],
                          [0          , 1, 0         ],
                          [-sin(theta), 0, cos(theta)]])
    
    rot = rot @ np.array([[1, 0, 0],
                          [0, cos(phi + pi), -sin(phi + pi)],
                          [0, sin(phi + pi), cos(phi + pi)]])

    # ------------ Orientation inside ECEF Reference Frame ------------ #
    orientation = Rotation.from_matrix(rot).as_rotvec(degrees=False)
    # ------------------------------------------------------------------ #

    return (PosX, PosY, PosZ), orientation


def create_message_header(callsign: str, msg_id: str, msg_len: int, requested_range_nm=100, reply_port=0):
    """
    Construct the Flightgear Multiplayer Protocol message header
    Source: https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py 

    Input:
        callsign:   str, callsign
        msg_id:     str, CHAT_MSG_ID or POS_DATA_ID
        msg_len:    int, Length of message
    
    Returns:
        header:     struct, header of FlightGear Multiplayer message
    """
    callsign_bytes = callsign.encode('ascii')[:8].ljust(8, b'\0')

    return struct.pack('!6I8s', MSG_MAGIC, PROTO_VER, msg_id, msg_len, requested_range_nm, reply_port, callsign_bytes)


def create_packet(callsign: str, actype: str, latitude: float, longitude: float, airspeed: float, altitude: float, phi: float, theta: float, psi: float):
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
    model = model_mapping(actype).encode('ascii')[:96].ljust(96, b'\0')
    fmt = '!96s2d3d3f3f3f3f3f'
    payload = struct.pack(fmt, model, time_val, lag, *position, *orientation, *linearVel, *angularVel, *linearAccel, *angularAccel)

    protocol_version = struct.pack('!h', 10) + struct.pack('!h', 2)
    squawk = struct.pack('!h', 1500) + struct.pack('!h', 1200)
    transponder_altitude = struct.pack('!h', 1501) + struct.pack('i', int(altitude / aero.ft))
    transponder_mode = struct.pack('!h', 1503) + struct.pack('!h', 2) # set to TA/RA so TCAS works
    transponder_airspeed = struct.pack('!h', 1505) + struct.pack('!h', int(airspeed / aero.kts))

    chat_message = f"{callsign}: JOINED FROM BLUESKY"
    chat = struct.pack('!HH', 10002, len(chat_message)) + chat_message.encode('utf-8')

                             # 4 bytes       
    pos_msg = payload + b'\x1f\xac\xe0\x02' + protocol_version 
    pos_msg += squawk + transponder_altitude + transponder_mode + transponder_airspeed #+ chat

    if len(pos_msg) % 4 != 0:
        pos_msg += b'\0' * (4 - (len(pos_msg) % 4))
    msg_len = 32 + len(pos_msg)
    header = create_message_header(callsign, POS_DATA_ID, msg_len)
    packet = header + pos_msg
    
    return packet