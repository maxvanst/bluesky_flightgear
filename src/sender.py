import socket
import time
import threading

from bluesky import traf

class FlightSimSender():
    """
    BlueSky -> Flightsim traffic sender
    """
    def __init__(self):
        self.is_sending = False
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.daemon = True

    def start(self):
        self.is_sending = True
        self.send_thread.start()

    def send(self):
        while True:
            if not self.is_sending:
                time.sleep(1.0)
                continue
            else:
                for callsign in traf.id:
                    # Send package w.r.t flightsim traffic protocol back to the simulator
                    pass