from bluesky import settings, stack, traf, sim
from plugins.flightgear.src.server.run import FlightGearServer
from plugins.flightgear.src.server.listener import FlightGearListener

class Core():
    """
    BlueSky FlightGear plugin Core
    """
    def __init__(self):
        self.server = FlightGearServer()
        self.listener = FlightGearListener()

    def toggle(self, flag):
        if flag:
            self.server.start()
            self.listener.start()

    def update(self):
        print(f"Connected clients: {self.listener.clients}")
