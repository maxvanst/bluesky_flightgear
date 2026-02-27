import struct
import math
import time
import numpy as np
from plugins.flightgear.src.server.acmap import model_mapping
from math import sqrt, radians, sin, cos, acos
from scipy.spatial.transform import Rotation

# Multiplayer Protocol Constants
MSG_MAGIC = 0x46474653  
PROTO_VER = 0x00010001
POS_DATA_ID = 7

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

    rot = T_enu2ecef @ np.array([[cos(-psi + math.pi/2), -sin(-psi + math.pi/2), 0],
                                 [sin(-psi + math.pi/2),  cos(-psi + math.pi/2), 0],
                                 [0, 0, 1]])
    
    rot = rot @ np.array([[cos(theta) , 0, sin(theta)],
                          [0          , 1, 0         ],
                          [-sin(theta), 0, cos(theta)]])
    
    rot = rot @ np.array([[1, 0, 0],
                          [0, cos(phi + math.pi), -sin(phi + math.pi)],
                          [0, sin(phi + math.pi), cos(phi + math.pi)]])

    # ------------ Orientation inside ECEF Reference Frame ------------ #
    orientation = Rotation.from_matrix(rot).as_rotvec(degrees=False)
    # ------------------------------------------------------------------ #

    return (PosX, PosY, PosZ), orientation


def create_message_header(callsign: str, msg_id: str, msg_len: int, requested_range_nm=100, reply_port=0):
    """
    Construct the Flightgear Multiplayer Protocol message header
    Source: https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py 
    """
    callsign_bytes = callsign.encode('ascii')[:8]
    callsign_bytes = callsign_bytes.ljust(8, b'\0')

    return struct.pack('!6I8s', MSG_MAGIC, PROTO_VER, msg_id, msg_len, requested_range_nm, reply_port, callsign_bytes)


def create_packet(callsign: str, actype: str, latitude: float, longitude: float, altitude: float, phi: float, theta: float, psi: float):
    """
    Create Flightgear Multiplayer Protocol UDP Packet
    * Positions, Orientations, Velocities and Accelerations are w.r.t. the Earth-Centered, Earth-Fixed frame.
    Source 1: https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py  
    Source 2: https://wiki.flightgear.org/Multiplayer_protocol
    """
    time_val = time.time()
    lag = 0
    linearVel = (0, 0, 0)
    angularVel = (0, 0, 0)
    linearAccel = (0, 0, 0)
    angularAccel = (0, 0, 0)
    position, orientation = bluesky2ecef(altitude, latitude, longitude, phi, theta, psi)
    v2_properties = [
        (10, 2, 'short') # TODO: Add more properties that might be of interest to BlueSky/FlightGear
    ]
    model_str = model_mapping(actype)
    model = model_str.encode('ascii')[:96]
    model = model.ljust(96, b'\0')
    fmt = '!96s2d3d3f3f3f3f3f'
    payload = struct.pack(fmt, model, time_val, lag, *position, *orientation, *linearVel, *angularVel, *linearAccel, *angularAccel)

    v2_block = b''
    for prop_id, value, enc in v2_properties:
        if enc == 'short':
            v2_block += struct.pack('!HH', prop_id, 2)  # LEN=2 bytes
            v2_block += struct.pack('!h', value)
        elif enc == 'int':
            v2_block += struct.pack('!HH', prop_id, 4)  # LEN=4 bytes
            v2_block += struct.pack('!i', value)
        elif enc == 'float':
            v2_block += struct.pack('!HH', prop_id, 4)  # LEN=4 bytes
            v2_block += struct.pack('!f', value)
        elif enc == 'string':
            if isinstance(value, str) and value:
                s = value.encode('utf-8')
                length = len(s)
                v2_block += struct.pack('!HH', prop_id, length)
                v2_block += s

    pos_msg = payload + v2_block
    if len(pos_msg) % 4 != 0:
        pos_msg += b'\0' * (4 - (len(pos_msg) % 4))
    header_len = 32
    msg_len = header_len + len(pos_msg)
    header = create_message_header(callsign, POS_DATA_ID, msg_len)
    packet = header + pos_msg
    
    return packet