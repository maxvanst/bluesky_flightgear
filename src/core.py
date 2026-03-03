from bluesky import settings, stack, traf, sim
from plugins.flightsim.src.flightgear.server import FlightGearServer
from plugins.flightsim.src.flightgear.listener import FlightGearListener

class Core():
    """
    BlueSky FlightGear plugin Core
    """
    def __init__(self, version):
        self.server = FlightGearServer()
        self.listener = FlightGearListener()

    def toggle(self, flag):
        if flag:
            self.server.start()
            self.listener.start()

    def update(self):
        print(f"Connected clients: {self.listener.clients}")