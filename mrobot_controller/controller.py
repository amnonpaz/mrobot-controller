import asyncio
import logging
from .websocket import WebSocketServer, WebSocketMessageHandler
from .deserializer import Deserializer
from .video_streamer import VideoStreamer


class Controller(WebSocketMessageHandler):
    def __init__(self, port: int, video_config: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.websocket_server = WebSocketServer(self, host='localhost', port=port)
        self.video_streamer = VideoStreamer(video_config['device'],
                                            video_config['width'],
                                            video_config['height'],
                                            'localhost',
                                            video_config['port'],
                                            video_config['test'])
        self.deserializer = Deserializer()
        self.event_loop = None
        self.tasks = None

        self.commands = {
            'video_start': self.video_start,
            'video_stop': self.video_stop
        }

    def handle_message(self, message):
        self.logger.info(f'received: {message}')
        try:
            command, parameters = self.deserializer.deserialize(message)
            try:
                self.commands[command](parameters)
            except KeyError as e:
                self.logger.warning(f'No such command: {e}')

        except KeyError:
            self.logger.warning('received malformed message')

    async def run(self):
        self.logger.debug('Starting server')

        self.event_loop = asyncio.get_running_loop()

        self.logger.debug('Server execution ends')

        self.tasks = await asyncio.gather(
            asyncio.to_thread(self.video_streamer.start),
            asyncio.create_task(self.websocket_server.start())
        )

    def stop(self):
        self.video_streamer.stop()
        self.tasks.cancel()

    def video_start(self, parameters):
        self.logger.info(f'Starting video')
        try:
            host = parameters['host']
            port = parameters['port']
        except KeyError as e:
            self.logger.warning(f'\"Start video\" parameters error: {e}')
            return
        self.video_streamer.host_set(host, port)

    def video_stop(self, _):
        self.logger.info(f'Stopping video')
        self.video_streamer.host_remove()
