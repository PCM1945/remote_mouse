import pyautogui
import win32api
import win32con
import asyncio
from window.schemas.monitor import Monitor
class MouseMonitorService:
    def __init__(self, border_threshold=1):
        self.clients = set()
        self.border_threshold = border_threshold
        self.previous_edges = set()
        self.current_monitor = None
        self.current_edges = set()
        self.current_pos = (0, 0)
        self._running = True
        self._edge_callbacks = []

    def subscribe_on_edge(self, callback):
        self._edge_callbacks.append(callback)

    def notify_edge_hit(self, edge):
        for callback in self._edge_callbacks:
            callback(edge, self.current_pos, self.current_monitor)

    def get_mouse_position(self):
        return pyautogui.position()

    def get_monitor_under_mouse(self):
        x, y = self.get_mouse_position()
        hmonitor = win32api.MonitorFromPoint((x, y), win32con.MONITOR_DEFAULTTONEAREST)
        info = win32api.GetMonitorInfo(hmonitor)
        return Monitor(*info["Monitor"])

    def detect_edges(self, x, y, monitor):
        edges = set()
        if x <= monitor.left + self.border_threshold:
            edges.add("LEFT")
        if x >= monitor.right - self.border_threshold:
            edges.add("RIGHT")
        if y <= monitor.top + self.border_threshold:
            edges.add("TOP")
        if y >= monitor.bottom - self.border_threshold:
            edges.add("BOTTOM")
        return edges

    async def run(self):
        while self._running:
            x, y = self.get_mouse_position()
            self.current_pos = (x, y)
            monitor = self.get_monitor_under_mouse()
            self.current_monitor = monitor
            current_edges = self.detect_edges(x, y, monitor)

            for edge in current_edges - self.previous_edges:
                self.notify_edge_hit(edge)

            self.previous_edges = current_edges
            self.current_edges = current_edges
            await asyncio.sleep(0.01)
        raise SystemExit(1)

    def stop(self):
        print('stopping monitor service')
        self._running = False