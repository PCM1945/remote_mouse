import time
import socket
from zeroconf import Zeroconf, ServiceBrowser
from browser_service import ZeroconfServiceListener, ServiceRegistry
import asyncio

async def main():
    registry = ServiceRegistry()
    service_type = "_http._tcp.local."
    zeroconf = Zeroconf()
    listener = ZeroconfServiceListener(registry, service_type)

    print("Searching for services...")
    browser = ServiceBrowser(zeroconf, service_type, listener)

    try:
        # Wait a few seconds to discover services
        await asyncio.sleep(3)

        services = registry.get_all()
        if not services:
            print("No services found.")
            return

        print("\nAvailable services:")
        for idx, svc in enumerate(services):
            print(f"[{idx}] {svc}")

        choice = int(input("Select a service to connect: "))
        selected = services[choice]

        # Connect via socket
        with socket.create_connection((selected.address, selected.port), timeout=5) as sock:
            data = sock.recv(1024)
            print(f"Received: {data.decode()}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        zeroconf.close()


if __name__ == "__main__":
    asyncio.run(main())
