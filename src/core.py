from bluesky import settings, stack, traf, sim
from plugins.flightgear.src.server.run import Server
from plugins.flightgear.src.aircraft import Aircraft

class Core():
    """
    BlueSky FlightGear plugin Core
    """
    def __init__(self):
        self.server = Server()

    def toggle(self, flag):
        if flag:
            self.server.start()

    def update(self):
        for callsign, param in list(self.server.listen_buffer.items()):
            aircraft = Aircraft(callsign, param)
            if traf.id2idx(callsign) < 0:
                aircraft.create()
            else:
                aircraft.move()
