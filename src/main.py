import asyncio
from services.monitor_service import MouseMonitorService
from services.ipc_service import IPCWebSocketServer
from ui.tray_app import TrayApp

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    service = MouseMonitorService(border_threshold=1)
    ipc = IPCWebSocketServer()

    def handle_edge_hit(edge, pos, monitor):
        asyncio.run_coroutine_threadsafe(
            ipc.broadcast({
                "event": "edge_hit",
                "edge": edge,
                "position": {"x": pos[0], "y": pos[1]},
                "monitor": monitor.to_dict()
            }),
            loop
        )

    service.subscribe_on_edge(handle_edge_hit)
    tray = TrayApp(monitor=service)
    tray.start()

    loop.create_task(service.run())
    loop.create_task(ipc.start())
    loop.run_forever()

if __name__ == "__main__":
    main()