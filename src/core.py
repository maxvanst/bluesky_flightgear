from bluesky import settings, stack, traf, sim
from plugins.flightsim.src.server.server import FlightGearServer
from plugins.flightsim.src.server.listener import FlightGearListener
from plugins.flightsim.src.gui.window import GUI

class Core():
    """
    BlueSky FlightGear plugin Core
    """
    def __init__(self, version):
        self.server = FlightGearServer()
        self.listener = FlightGearListener()
        #self.gui = GUI(version)

    def toggle(self, flag):
        if flag:
            self.server.start()
            self.listener.start()

    def update(self):
        print(f"Connected clients: {self.listener.clients}")