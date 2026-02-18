import time
from bluesky import stack
from bluesky.tools import aero

class Aircraft():
    def __init__(self):
        self.ts: float
        self.state = {}
        self.state_prev = {}
        self.address: str
        self.address: str
        self.squawk: int
        self.actype: str
        self.ident: int
        self.altitude: int
        self.airspeed: int
        self.vertical: float
        self.heading: float
        self.latitude: float
        self.longitude: float
        self.origin: str
        self.destination: str

    def set_state(self, state):
        self.ts = time.time()
        self.state = state
        self.callsign = state["callsign"]
        self.squawk = state["squawk"]
        self.actype = state["actype"]
        self.ident = state["ident"]
        self.altitude = state["altitude"]
        self.airspeed = state["airspeed"]
        self.vertical_speed = state["vertical_speed"]
        self.heading = state["heading"]
        self.latitude = state["latitude"]
        self.longitude = state["longitude"]
        self.origin = state["origin"]
        self.destination = state["destination"]

    def set_prev_state(self, state):
        self.state_prev = state

    def check_update_state(self):
        if len(self.state_prev) != 0: 
            for state_name in ["ident", "squawk"]:
                if self.state[state_name] != self.state_prev[state_name]:
                    # ------------------------ ATC ------------------------ #
                    if state_name == "ident" and self.state[state_name] == True:
                        cmdstr = f"COLOR {self.callsign},251,3,255"
                        stack.stack(cmdstr)
                    if state_name == "ident" and self.state[state_name] == False:
                        cmdstr = f"COLOR {self.callsign},0,255,0"
                        stack.stack(cmdstr)

                    print(f"[FLIGHTGEAR] - {state_name} CHANGED FROM {self.state_prev[state_name]} TO {self.state[state_name]}!")

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

    # # ----------------- FlightPlan ---------------- #
    # def set_flightplan_origin(self):
    #     cmdstr = "ORIG %s, %s" % (self.callsign, self.origin)
    #     stack.stack(cmdstr)

    # def set_flightplan_destination(self):
    #     cmdstr = "DEST %s, %s" % (self.callsign, self.destination)
    #     stack.stack(cmdstr)





















    # # ----------------- FlightPlan ---------------- #
    # def flightplan_set_origin(self, ac):
    #     cmdstr = "ORIG %s, %s" % (ac["callsign"], ac["origin"])
    #     stack.stack(cmdstr)

    # def flightplan_set_destination(self, ac):
    #     cmdstr = "DEST %s, %s" % (ac["callsign"], ac["destination"])
    #     stack.stack(cmdstr)

    # # -------------------- ATC -------------------- #
    # def ident(self, ac):
    #     cmdstr = f"COLOR {ac["callsign"]},251,3,255"
    #     stack.stack(cmdstr)

    # def unident(self, ac):
    #     cmdstr = f"COLOR {ac["callsign"]},0,255,0"
    #     stack.stack(cmdstr)