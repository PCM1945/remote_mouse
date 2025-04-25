from zeroconf import Zeroconf, ServiceInfo
import socket
from networkconfig import NetworkConfig


class ZeroconfService:
    def __init__(self, service_name: str, service_type: str, config: NetworkConfig):
        self.zeroconf = Zeroconf()
        self.config = config
        self.service_info = ServiceInfo(
            type_=service_type,
            name=f"{service_name}.{service_type}",
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            port=config.port,
            properties={},
            server=socket.gethostname() + ".local."
        )

    def register(self):
        self.zeroconf.register_service(self.service_info)
        print(f"Zeroconf service '{self.service_info.name}' registered on port {self.config.port}")

    def unregister(self):
        self.zeroconf.unregister_service(self.service_info)
        self.zeroconf.close()
        print(f"Zeroconf service '{self.service_info.name}' unregistered")
