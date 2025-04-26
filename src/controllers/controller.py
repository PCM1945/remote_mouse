import asyncio
from services.monitor_service import MouseMonitorService
from services.cursor_sender import CursorSender

class Controller:
    def __init__(self, get_target, edge='RIGHT'):
        self.get_target = get_target
        self.edge = edge
        self.monitor = MouseMonitorService(callback=self._on_edge_hit, edge=self.edge)
        self.sender = CursorSender(get_target=self.get_target, is_active=self._should_send)
        self.sending = False

    def _on_edge_hit(self):
        print(f"[Controller] Borda {self.edge} tocada, iniciando envio de posição")
        self.sending = True

    def _should_send(self):
        return self.sending

    async def start(self):
        monitor_task = asyncio.create_task(self.monitor.start())
        sender_task = asyncio.create_task(self.sender.start())

        await asyncio.gather(monitor_task, sender_task)

    def stop(self):
        self.monitor.stop()
        self.sender.stop()
        self.sending = False