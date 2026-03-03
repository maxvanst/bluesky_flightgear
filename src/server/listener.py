import time
import socket
import threading
import numpy as np

from bluesky import stack, settings, traf
from bluesky.core import Entity, timed_function
from bluesky.tools import aero
from bluesky import scr

class FlightGearListener(Entity):
    def __init__(self):
        super().__init__()
        self.clients = {}
        self.is_listening = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.buffer = {}

        with self.settrafarrays():
            self.squawk = np.array([])
            self.ident = np.array([])

    def start(self):
        self.is_listening = True
        self.socket.bind(("localhost", 5000))
        self.thread.start()
    
    def listen(self):
        while True:
            if not self.is_listening:
                time.sleep(1.0)
                continue
            else:
                data, address = self.socket.recvfrom(1024)
                decoded = data.decode('utf-8').replace('"', '').split(";")
                client = str(decoded[0])
                address = str(decoded[1])
                callsign = str(decoded[2])
                timestamp = time.time()
                flight = {'ts': timestamp,
                          'squawk': str(decoded[3]),
                          'actype': str(decoded[4]),
                          'ident': bool(int(decoded[5])),
                          'altitude': int(decoded[6]),
                          'airspeed': int(decoded[7]),
                          'vertical_speed': float(decoded[8]),
                          'heading': float(decoded[9]),
                          'latitude': float(decoded[10]),
                          'longitude': float(decoded[11])}
                
                self.clients[client] = {'timestamp': timestamp, 'address': address, 'callsign': callsign}
                self.buffer[callsign] = flight

    @timed_function(name='FGLISTENER', dt=0.0)
    def update(self):
        if not self.is_listening:
            return
        
        for callsign, param in list(self.buffer.items()):
            idx = traf.id2idx(callsign)
            actype = str(param['actype'])
            latitude = float(param['latitude'])
            longitude = float(param['longitude'])
            heading = int(param['heading'])
            altitude = int(param["altitude"]) * aero.ft
            airspeed =  aero.tas2cas(int(param['airspeed']), altitude * aero.ft)
            vertical_speed = float(param['vertical_speed'])

            if traf.id2idx(callsign) < 0:
                traf.cre(callsign, actype, latitude, longitude, heading, altitude, airspeed)
            else:
                traf.move(idx, latitude, longitude, altitude, heading, airspeed, vertical_speed)
                self.squawk[idx] = int(param['squawk'])
                self.ident[idx] = param['ident']

                # Check IDENT
                if self.ident[idx]:
                    stack.stack(f"COLOR {callsign},{scr.red}")
                else:
                    stack.stack(f"COLOR {callsign},0,255,0")

                # Check special SQUAWK codes
                if self.squawk[idx] == 7500: # Hijack
                    stack.stack(f"COLOR {callsign},255,0,0")
                    stack.stack(f"ECHO HIJACK: {callsign} SQUAWK 7500")

                if self.squawk[idx] == 7600: # Radio failure
                    stack.stack(f"COLOR {callsign},255,0,0")
                    stack.stack(f"ECHO RADIO FAIL: {callsign} SQUAWK 7600")

                if self.squawk[idx] == 7700: # Emergency
                    stack.stack(f"COLOR {callsign},255,0,0")
                    stack.stack(f"ECHO EMERGENCY: {callsign} SQUAWK 7700")