from plugins.flightgear.aircraft import Aircraft

class Traffic():
    def __init__(self):
        self.aircraft = Aircraft()
        self.show_flightgear_aircraft_in_bluesky = True

    def update(self, flights):
        if self.show_flightgear_aircraft_in_bluesky:
            for i, ac in list(flights.items()):
                if not self.aircraft.exists(ac):
                    self.aircraft.create(ac)
                else:
                    self.aircraft.move(ac)