import asyncio
import websockets
import logging
from abc import ABC, abstractmethod


class WebSocketMessageHandler(ABC):
    @abstractmethod
    async def handle_message(self, message):
        pass


class CatMessageHandler(WebSocketMessageHandler):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    async def handle_message(self, message):
        self.logger.info(f"Handling message: {message}")


class WebSocketServer:
    def __init__(self, message_handler: WebSocketMessageHandler, host='localhost', port=8765):
        if not isinstance(message_handler, WebSocketMessageHandler):
            raise TypeError("handler must be an instance of MessageHandler")

        self.logger = logging.getLogger(self.__class__.__name__)

        self.host = host
        self.port = port
        self.client = None
        self.message_handler = message_handler

    async def register(self, websocket):
        if self.client is not None:
            await websocket.close(code=websockets.exceptions.ConnectionClosedError, reason="Only one client allowed")
            self.logger.warning(f"Rejected connection from {websocket.remote_address}, already one client connected")
        else:
            self.client = websocket
            self.logger.info(f"Client connected: {websocket.remote_address}")

    async def unregister(self, websocket):
        if self.client == websocket:
            self.logger.info(f"Client disconnected: {websocket.remote_address}")
            self.client = None

    async def send(self, message):
        if self.client is not None:
            await self.client.send(message)
            self.logger.debug(f"Sent message to client: {message}")
        else:
            self.logger.warning("No client connected to send the message to")

    async def serve(self, websocket, path):
        await self.register(websocket)
        if self.client is websocket:
            try:
                async for message in websocket:
                    self.logger.debug(f"Received message: {message}")
                    await self.message_handler.handle_message(message)
            except websockets.exceptions.ConnectionClosed as e:
                self.logger.error(f"Connection closed: {websocket.remote_address} - {e}")
            finally:
                await self.unregister(websocket)

    async def start(self):
        server = await websockets.serve(self.serve, self.host, self.port)
        self.logger.info(f"Server started on ws://{self.host}:{self.port}")
        await server.wait_closed()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )

    handler = CatMessageHandler()
    ws_server = WebSocketServer(message_handler=handler)
    asyncio.run(ws_server.start())
