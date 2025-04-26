import asyncio
import json
import pyautogui

class CursorReceiver:
    def __init__(self, host='0.0.0.0', port=8989):
        self.host = host
        self.port = port
        self.server = None
        self.active = False

    async def start(self):
        self.server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        addr = self.server.sockets[0].getsockname()
        print(f"[Receiver] Escutando em {addr}")
        self.active = True

        async with self.server:
            await self.server.serve_forever()

    async def _handle_client(self, reader, writer):
        try:
            data = await reader.readline()
            message = data.decode().strip()
            coords = json.loads(message)
            x, y = coords.get("x"), coords.get("y")

            if x is not None and y is not None:
                pyautogui.moveTo(x, y)

        except Exception as e:
            print(f"[Receiver] Erro ao receber dados: {e}")
        finally:
            writer.close()
            await writer.wait_closed()