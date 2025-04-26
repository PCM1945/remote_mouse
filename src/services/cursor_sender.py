import asyncio
import socket
import json
import pyautogui

class CursorSender:
    def __init__(self, get_target, is_active, interval=0.01):
        """
        get_target: função que retorna (ip, porta) do destino selecionado.
        is_active: função que retorna True se o envio deve ocorrer.
        """
        self.get_target = get_target
        self.is_active = is_active
        self.interval = interval
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            if self.is_active():
                x, y = pyautogui.position()
                await self._send_position(x, y)
            await asyncio.sleep(self.interval)

    def stop(self):
        self.running = False

    async def _send_position(self, x, y):
        target = self.get_target()
        if not target:
            return

        ip, port = target
        message = json.dumps({'x': x, 'y': y}).encode()
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            writer.write(message + b"\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"[Sender] Erro ao enviar: {e}")