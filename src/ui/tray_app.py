from pystray import Icon, MenuItem, Menu
from PIL import Image
import threading
import asyncio
import websockets
from plyer import notification
import json
from pathlib import Path
from services.monitor_service import MouseMonitorService

CONFIG_PATH = Path("./.mouse_monitor_config.json")

DEFAULT_EDGES = set()

if not CONFIG_PATH.exists():
    with open(CONFIG_PATH, "w") as file:
        json.dump({"selected_edges": []}, file, indent=4)

class TrayApp:
    def __init__(self,  ws_url="ws://localhost:8765/ws", monitor:MouseMonitorService = None):
        self.monitor = monitor
        self.ws_url = ws_url
        self.edges = {"LEFT", "RIGHT", "TOP", "BOTTOM"}
        self.selected_edges = self.load_config()
        self.latest_event = "No events yet"
        self.icon = None
        self._running = True

    def load_config(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    return set(data.get("selected_edges", []))
            except Exception as e:
                print(f"Failed to load config: {e}")
        return DEFAULT_EDGES

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({
                    "selected_edges": list(self.selected_edges)
                }, f)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def toggle_edge(self, edge):
        def _toggle(icon, item):
            if item.checked:
                self.selected_edges.discard(edge)
            else:
                self.selected_edges.add(edge)
            self.save_config()
        return _toggle

    def draw_icon(self):
        return Image.open('./assets/tray.ico')

    def on_quit(self, icon, item):
        self._running = False
        icon.stop()
        self.monitor.stop()

    
    def edge_config_menu(self):
        submenu = []
        for edge in self.edges:
            submenu.append(MenuItem(
                edge,
                self.toggle_edge(edge),
                checked=lambda item, edge=edge: edge in self.selected_edges
            ))
        return Menu(*submenu)

    def build_menu(self):
        return Menu(
            MenuItem("Select Edges", self.edge_config_menu()),
            MenuItem("Quit", self.on_quit)
        )

    def run_icon(self):
        self.icon = Icon("EdgeMonitor", icon=self.draw_icon(), menu=self.build_menu())
        self.icon.run()

    def start_ws_listener(self):
        async def listen():
            while self._running:
                try:
                    async with websockets.connect(self.ws_url) as websocket:
                        async for message in websocket:
                            data = json.loads(message)
                            if data.get("event") == "edge_hit":
                                edge = data["edge"]
                                x, y = data["position"]["x"], data["position"]["y"]
                                mon = data["monitor"]
                                self.latest_event = f"Mouse hit {edge} edge at ({x}, {y})"
                                if data['edge'] in self.selected_edges:
                                    print(self.latest_event)
                                else:
                                    continue
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    await asyncio.sleep(2)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(listen())

    def start(self):
        threading.Thread(target=self.run_icon, daemon=True).start()
        threading.Thread(target=self.start_ws_listener, daemon=True).start()
