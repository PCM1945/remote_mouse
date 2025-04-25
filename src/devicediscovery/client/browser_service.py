from zeroconf import Zeroconf, ServiceListener
import socket
from typing import Dict


class DiscoveredService:
    def __init__(self, name: str, address: str, port: int):
        self.name = name
        self.address = address
        self.port = port

    def __str__(self):
        return f"{self.name} at {self.address}:{self.port}"


class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, DiscoveredService] = {}

    def add(self, service: DiscoveredService):
        self.services[service.name] = service

    def get_all(self):
        return list(self.services.values())

    def get_by_name(self, name: str):
        return self.services.get(name)


class ZeroconfServiceListener(ServiceListener):
    def __init__(self, registry: ServiceRegistry, service_type: str):
        self.registry = registry
        self.service_type = service_type

    def add_service(self, zeroconf: Zeroconf, type_: str, name: str):
        info = zeroconf.get_service_info(type_, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            port = info.port
            service = DiscoveredService(name, address, port)
            self.registry.add(service)
            print(f"Discovered: {service}")

    def remove_service(self, zeroconf: Zeroconf, type_: str, name: str):
        print(f"Service removed: {name}")

    def update_service(self, zeroconf: Zeroconf, type_: str, name: str):
        # Optionally handle updates
        pass
