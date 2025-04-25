import socket
from networkconfig import NetworkConfig
class SocketServer:
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.socket.bind((self.config.host, self.config.port))
        self.socket.listen()
        print(f"Socket server listening on {self.config.host}:{self.config.port}")

    def accept_connection(self):
        client_socket, addr = self.socket.accept()
        print(f"Connection accepted from {addr}")
        return client_socket, addr

    def close(self):
        self.socket.close()

