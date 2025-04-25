from aiohttp import web, WSMsgType
import json

class IPCWebSocketServer:
    def __init__(self):
        self.clients = set()

    async def register(self, ws):
        self.clients.add(ws)

    async def unregister(self, ws):
        self.clients.discard(ws)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for ws in list(self.clients):
            try:
                await ws.send_str(data)
            except Exception:
                self.clients.discard(ws)

    def create_app(self):
        app = web.Application()

        async def websocket_handler(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            await self.register(ws)

            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    if msg.data == "ping":
                        await ws.send_str("pong")
                elif msg.type == WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")

            await self.unregister(ws)
            return ws

        app.router.add_get("/ws", websocket_handler)
        return app

    async def start(self, host="localhost", port=8765):
        app = self.create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
