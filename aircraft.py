from bluesky import stack
from bluesky.tools import aero

class Aircraft():
    def __init__(self, callsign: str, param: dict):
        self.callsign = callsign
        self.actype = param["actype"]
        self.latitude = param["latitude"]
        self.longitude = param["longitude"]
        self.heading = param["heading"]
        self.altitude = param["altitude"]
        self.airspeed = param["airspeed"]
        self.vertical_speed = param["vertical_speed"]
    # -------------- General ----------------- #    
    def create(self):
        cmdstr = "CRE %s, %s, %f, %f, %f, %d, %f" % (
            self.callsign,
            self.actype,
            self.latitude,
            self.longitude,
            self.heading,
            self.altitude,
            self.airspeed
        )
        stack.stack(cmdstr)

    def delete(self):
        cmdstr = "DEL %s" % (self.callsign)
        stack.stack(cmdstr)
        
    # -------------- Movement ---------------- #
    def move(self):
        cmdstr = "MOVE %s, %f, %f, %d, %f, %f, %f" % (
            self.callsign,
            self.latitude,
            self.longitude,
            self.altitude,
            self.heading,
            aero.tas2cas(self.airspeed, self.altitude * aero.ft),
            self.vertical_speed
        )
        stack.stack(cmdstr)