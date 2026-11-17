# src/multiplayer/coordinates.py

import numpy as np
from scipy.spatial.transform import Rotation

# WGS84 ellipsoid parameters as defined in bluesky.tools.geo
a = 6378137.0                                                       # Semi-major axis [m]
b = 6356752.314245                                                  # Semi-minor axis [m]
e = np.sqrt(1 - (b**2)/(a**2))                                      # Eccentricity    [-]

def geodetic2ecef(alt: float, lat_deg: float, lon_deg: float, phi_deg: float, theta_deg: float, psi_deg: float):
    """
    Reference: https://en.wikipedia.org/wiki/Geographic_coordinate_conversion
               https://ahrs.readthedocs.io/en/latest/frames/geodetic2ecef.html

    Input:
        alt:        float, altitude [m]
        lat_deg:    float, latitude [deg]
        lon_deg:    float, longitude [deg]
        phi_deg:    float, roll angle [deg]
        theta_deg:  float, pitch angle [deg]
        psi_deg     float, yaw angle [deg]

    Returns:
        position:    tuple, position vector within ECEF reference frame
        orientation: tuple, orientation vector within ECEF reference frame
    """

    lat, lon = np.deg2rad(lat_deg), np.deg2rad(lon_deg)

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

    orientation = tuple(Rotation.from_matrix(rotation).as_rotvec(degrees=False))

    return position, orientation



def ecef2geodetic(position: tuple, orientation: tuple):
    """
    Reference: https://ahrs.readthedocs.io/en/latest/frames/ecef2geodetic.html

    Input:
        position:    tuple, position vector within ECEF reference frame
        orientation: tuple, orientation vector within ECEF reference frame

    Returns:
        alt:        float, altitude [m]
        lat_deg:    float, latitude [deg]
        lon_deg:    float, longitude [deg]
        psi_deg     float, yaw angle [deg]
        phi_deg:    float, roll angle [deg]
        theta_deg:  float, pitch angle [deg]
    """
    PosX, PosY, PosZ = position

    p = np.sqrt(PosX**2 + PosY**2)
    
    lon = np.arctan2(PosY, PosX)

    # Iteratively compute latitude
    lat = np.arctan2(PosZ, p * (1 - e**2))  # initial estimate, radians

    for _ in range(5):
        N = a / np.sqrt(1.0 - e**2 * np.sin(lat)**2)
        lat = np.arctan2(PosZ + e**2 * N * np.sin(lat), p)

    # position
    alt = p / np.cos(lat) - N
    lat_deg = np.rad2deg(lat)
    lon_deg = np.rad2deg(lon)

    T_ecef2ned = Rotation.from_euler('yz', [-(90 + lat_deg), lon_deg], degrees=True).as_matrix()
    rotation = Rotation.from_rotvec(np.array(orientation), degrees=False).as_matrix()

    T_ned2body = np.linalg.inv(T_ecef2ned) @ rotation

    psi_deg, phi_deg, theta_deg = Rotation.from_matrix(T_ned2body).as_euler('zyx', degrees=True) + (360, 0, 0)

    return alt, lat_deg, lon_deg, psi_deg, phi_deg, theta_deg