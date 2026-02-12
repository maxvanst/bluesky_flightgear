import time
import socket
import threading

# Copied and made small changes to TcpSocket ./tools/network.py from Bluesky
# Added UDP functionality in contrast to TCP

class UDPSocket:
    """
    UDP Client
    """
    def __init__(self):
        self.buffer_size = 1024
        self.is_connected = False
        self.receiver_thread = threading.Thread(target=self.receiver)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def isConnected(self):
        return self.is_connected

    def connectToHost(self, ip, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock.bind((ip, port))
            self.is_connected = True
            print("Connected to HOST: %s, PORT: %s" % (ip, port))
        except Exception as err:
            self.is_connected = False
            print("Connection Error: %s" % err)
            pass

    def disconnectFromHost(self):
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