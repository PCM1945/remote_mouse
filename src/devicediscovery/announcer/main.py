import signal
import sys
from zeroconf_service import ZeroconfService
from networkconfig import NetworkConfig
from socket_server import SocketServer

def main():
    config = NetworkConfig(port=5001)
    server = SocketServer(config)
    service = ZeroconfService("remote_mouse", "_http._tcp.local.", config)

    def cleanup(signum, frame):
        print("Shutting down...")
        service.unregister()
        server.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    service.register()
    server.start()

    while True:
        client_socket, addr = server.accept_connection()
        client_socket.sendall(b"Hello from Zeroconf Socket Server!\n")
        client_socket.close()


if __name__ == "__main__":
    main()