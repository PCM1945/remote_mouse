from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser
import socket
import threading

class DeviceDiscovery:
    def __init__(self, service_type="_mousemon._tcp.local.", port=8765):
        self.zeroconf = Zeroconf()
        self.service_type = service_type
        self.port = port
        self.services = {}
        self.lock = threading.Lock()

    def get_named_devices(self):
        with self.lock:
            return [(name, ip, port) for name, (ip, port) in self.services.items()]

    def start_advertising(self, name="MouseMonitor"):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        info = ServiceInfo(
            self.service_type,
            f"{name}.{self.service_type}",
            addresses=[socket.inet_aton(ip)],
            port=self.port,
            properties={},
            server=f"{hostname}.local.",
        )
        self.zeroconf.register_service(info)

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        if state_change.name == "ServiceStateChange.Added":
            info = zeroconf.get_service_info(service_type, name)
            if info:
                ip = socket.inet_ntoa(info.addresses[0])
                with self.lock:
                    self.services[name] = (ip, info.port)
        elif state_change.name == "ServiceStateChange.Removed":
            with self.lock:
                self.services.pop(name, None)

    def start_browsing(self):
        ServiceBrowser(self.zeroconf, self.service_type, handlers=[self.on_service_state_change])

    def get_devices(self):
        with self.lock:
            return list(self.services.values())

    def close(self):
        self.zeroconf.close()