import time
import socket
import threading

# Copied and made small changes to TcpSocket /bluesky/tools/network.py from Bluesky
# Added UDP functionality in contrast to TCP

from bluesky import settings, stack, traf
from bluesky.tools import aero

settings.set_variable_defaults(flightgear_host="127.0.0.1", flightgear_port=5501)

class FG_UDP_Listener:
    """
    UDP Listener for FlightGear using custom BlueSky protocol
    """
    def __init__(self):
        self.buffer_size = 1024
        self.is_connected = False
        self.receiver_thread = threading.Thread(target=self.receiver)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        self.acpool = {}

    def listenOnPort(self, ip, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock.bind((ip, port))
            self.is_connected = True
            print("Listening on HOST: %s, PORT: %s" % (ip, port))
        except Exception as err:
            self.is_connected = False
            print("Connection Error: %s" % err)
            pass

    def disconnectFromPort(self):
        try:
            self.sock.close()
            self.is_connected = False
            print("Disconnected")
        except Exception as err:
            print("Disconnection Error: %s" % err)
            pass

    def receiver(self):
        while True:
            if not self.is_connected:
                time.sleep(1.0)
                continue
            try:
                data, address = self.sock.recvfrom(self.buffer_size)
                self.processData(data, address)
                time.sleep(0.1)

            except Exception as err:
                print("Receiver Error: %s" % err)
                time.sleep(1.0)

    def processData(self, data, address):
        decoded = data.decode('utf-8').replace('"', '').split(";")
        flight = {'address': str(address),
                'callsign': 'PH-LAB',
                'squawk': str(decoded[0]),
                'actype': str(decoded[1]),
                'ident': bool(int(decoded[2])),
                'altitude': int(decoded[3]),
                'airspeed': int(decoded[4]),
                'vertical_speed': float(decoded[5]),
                'heading': float(decoded[6]),
                'latitude': float(decoded[7]),
                'longitude': float(decoded[8]),
                'origin': str(decoded[9]),
                'destination': str(decoded[10])}
                
        self.acpool[flight['callsign']] = flight

    def update(self):
        if self.is_connected:
            for i, ac in list(self.acpool.items()):
                acid = ac["callsign"]
                if traf.id2idx(acid) < 0:
                    # Create aircraft
                    cmdstr = "CRE %s, %s, %f, %f, %f, %d, %f" % (
                        acid,
                        ac["actype"],
                        ac["latitude"],
                        ac["longitude"],
                        ac["heading"],
                        ac["altitude"],
                        0.0
                    )
                    stack.stack(cmdstr)

                else:
                    # Update aircraft
                    cmdstr = "MOVE %s, %f, %f, %d, %f, %f, %f" % (
                        acid,
                        ac["latitude"],
                        ac["longitude"],
                        ac["altitude"],
                        ac["heading"],
                        aero.tas2cas(ac["airspeed"], ac["altitude"] * aero.ft),
                        ac["vertical_speed"]
                    )
                    stack.stack(cmdstr)

                    # Check if Aircraft is using IDENT
                    if ac["ident"]:
                        #cmdstr = "IDENT %s"
                        #stack.stack(cmdstr)
                        print("IDENT ON")

                    # FlightPlan
                    if ac["origin"] != "":
                        cmdstr = "ORIG %s, %s" % (acid, ac["origin"])
                        stack.stack(cmdstr)

                    if ac["destination"] != "":
                        cmdstr = "DEST %s, %s" % (acid, ac["destination"])
                        stack.stack(cmdstr)

        return 

    def toggle(self, flag=None):
        if flag is None:
            if self.is_connected:
                print(f"Listening on {settings.flightgear_host} on port {settings.flightgear_port}")
            else:
                print("Not connected")
        elif flag:
            self.listenOnPort(settings.flightgear_host, settings.flightgear_port)
        else:
            self.disconnectFromPort()