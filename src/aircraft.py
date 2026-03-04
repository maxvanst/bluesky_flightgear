import time

class FlightSimAircraft():
    def __init__(self, address: str, simname: str, callsign: str, alpha: float, beta: float, gamma: float, phi: float, theta: float, psi: float, latitude:float, longitude: float, altitude: float, true_airspeed: float, vertical_speed: float):
        """
        FlightSimAircraft class

        Input:
            -------- Network -------
            address:        IP + port
            simtype:        Name of Flight Simulator

            -------- General -------
            callsign:       Callsign of Aircraft

            -------- Angles --------
            alpha:          Angle of Attack [deg]
            beta:           Sideslip angle [deg]
            gamma:          Flight path angle [deg]
            phi:            Roll angle [deg]
            theta:          Pitch angle [deg]
            psi:            Yaw angle [deg]

            ------- Position ------
            latitude:       Latitude [deg]
            longitude:      Longitude [deg]
            altitude:       Altitude [m]

            -------- Speed --------
            true_airspeed:  True Airpseed [m/s]
            vertical_speed: Verticial Speed [m/s]
        """
        # Network
        self.address = address
        self.simtype = simname
        
        # General
        self.ts_created = time.time() # Creation timestamp
        self.callsign = self.callsign

        # Angles
        self.alpha = alpha 
        self.beta = beta   
        self.gamma = gamma 
        self.phi = phi     
        self.theta = theta 
        self.psi = psi     

        # Position
        self.latitude = latitude 
        self.longitude = longitude 

        # Altitude
        self.altitude = altitude
        
        # Speed
        self.true_airspeed = true_airspeed 
        self.vertical_speed = vertical_speed 