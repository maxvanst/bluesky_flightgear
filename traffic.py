from bluesky import traf
from plugins.flightgear.aircraft import Aircraft

class Traffic():
    def __init__(self):
        self.show_flightgear_aircraft_in_bluesky = True
        self.flights: dict[str, Aircraft] = {}

    def update(self, buffer):
        if self.show_flightgear_aircraft_in_bluesky:
            for address, flight in list(buffer.items()):
                callsign = flight["callsign"]
                if traf.id2idx(callsign) < 0:
                    # Aircraft is not existing [BlueSky] -> create
                    aircraft = Aircraft()
                    aircraft.set_state(flight)
                    aircraft.create()
                    self.flights[callsign] = aircraft
                else:
                    # Aircraft already exists [BlueSky]
                    aircraft = self.flights[callsign]
                    aircraft.set_state(flight)
                    aircraft.check_update_state()
                    aircraft.move()
                    aircraft.set_prev_state(flight)
            