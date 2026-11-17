# src/multiplayer/server.py

# General imports
import time
import socket
import threading

# Plugin imports
from .protocol import FlightGearMultiplayerPacket

class FlightGearMultiplayerServer:
    """FlightGear Multiplayer Server is responsible for receiving (decoding) and sending (encoding) FlightGear multiplayer UDP packets."""
    def __init__(self, receive_interface: str, receive_port: int, send_interface: str, send_port: int):
        self._listener = False

        # Listen
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.listen_socket.bind((receive_interface, receive_port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.listen_buffer = {}

    def listen(self) -> None:
        while True:
            if not self._listener :
                time.sleep(1.0)
                continue
            else:
                data, address = self.listen_socket.recvfrom(1024)
                header = (data[:4]).decode('utf-8')
                if header == 'FGFS':
                    aircraft = FlightGearMultiplayerPacket.decode(data)
                    print(time.time(), aircraft.callsign)
                    