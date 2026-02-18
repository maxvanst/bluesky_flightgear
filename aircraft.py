from bluesky import stack, traf
from bluesky.tools import aero

class Aircraft():
    def __init__(self):
        pass

    # -------------- General ----------------- #
    def exists(self, ac, existence=False):
        if not traf.id2idx(ac["callsign"]) < 0:
            existence = True
        return existence

    # -------------- Movement ---------------- #
    def create(self, ac):
        cmdstr = "CRE %s, %s, %f, %f, %f, %d, %f" % (
            ac["callsign"],
            ac["actype"],
            ac["latitude"],
            ac["longitude"],
            ac["heading"],
            ac["altitude"],
            0.0
        )
        stack.stack(cmdstr)

    def delete(self, ac):
        cmdstr = "DEL %s" % (ac["callsign"])
        stack.stack(cmdstr)

    def move(self, ac):
        cmdstr = "MOVE %s, %f, %f, %d, %f, %f, %f" % (
            ac["callsign"],
            ac["latitude"],
            ac["longitude"],
            ac["altitude"],
            ac["heading"],
            aero.tas2cas(ac["airspeed"], ac["altitude"] * aero.ft),
            ac["vertical_speed"]
        )
        stack.stack(cmdstr)

    # ----------------- FlightPlan ---------------- #
    def flightplan_set_origin(self, ac):
        cmdstr = "ORIG %s, %s" % (ac["callsign"], ac["origin"])
        stack.stack(cmdstr)

    def flightplan_set_destination(self, ac):
        cmdstr = "DEST %s, %s" % (ac["callsign"], ac["destination"])
        stack.stack(cmdstr)

    # -------------------- ATC -------------------- #
    def ident(self, ac):
        cmdstr = f"COLOR {ac["callsign"]},251,3,255"
        stack.stack(cmdstr)

    def unident(self, ac):
        cmdstr = f"COLOR {ac["callsign"]},0,255,0"
        stack.stack(cmdstr)

