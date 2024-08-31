import asyncio
import logging
from .websocket import WebSocketServer, WebSocketMessageHandler
from .deserializer import Deserializer
from .video_streamer import VideoStreamer


class Controller(WebSocketMessageHandler):
    def __init__(self, port: int):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.websocket_server = WebSocketServer(self, host='localhost', port=port)
        self.video_streamer = None
        self.deserializer = Deserializer()

    def handle_message(self, message):
        self.logger.info(f'received: {message}')
        try:
            command, parameters = self.deserializer.deserialize(message)
        except KeyError:
            self.logger.warning('received malformed message')

    def start(self):
        self.logger.debug('Starting server')
        asyncio.run(self.websocket_server.start())
        self.logger.debug('Server execution ends')

    def stop(self):
        pass
