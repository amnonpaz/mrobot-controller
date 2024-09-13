import asyncio
import logging
from .websocket import WebSocketServer, WebSocketMessageHandler
from .serdes import deserialize, DeserializationError, serialize
from .video_streamer import VideoStreamer
from .dns_sd import ServicePublisher


class ControllerException(Exception):
    pass


class Controller(WebSocketMessageHandler):
    def __init__(self, port: int, video_config: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.service_publisher = ServicePublisher('mrobot-server', port)
        self.websocket_server = WebSocketServer(self, hosts=self.service_publisher.get_ips(), port=port)
        self.video_streamer = VideoStreamer(video_config['device'],
                                            video_config['width'],
                                            video_config['height'],
                                            'localhost',
                                            video_config['port'],
                                            video_config['test'])
        self.event_loop = None
        self.tasks = None

        self.commands = {
            'video_start': self.video_start,
            'video_stop': self.video_stop
        }

    def handle_message(self, message):
        success = False
        try:
            command, parameters = deserialize(message)
            response = self.commands[command](parameters)
            success = True
        except KeyError as e:
            self.logger.warning(f'Invalid command: {e}')
            response = f'Invalid command: {e}'
        except ControllerException as e:
            self.logger.warning(f'Command failed: {e}')
            response = str(e)
        except DeserializationError as e:
            self.logger.warning(f'received malformed message: {e}')
            response = str(e)

        return serialize({'success': success, 'response': response})

    async def run(self):
        self.logger.debug('Starting server')

        self.service_publisher.publish()

        self.event_loop = asyncio.get_running_loop()
        self.tasks = await asyncio.gather(
            asyncio.to_thread(self.video_streamer.start),
            asyncio.create_task(self.websocket_server.start())
        )

    def stop(self):
        if self.service_publisher:
            self.service_publisher.unpublish()
        if self.video_streamer:
            self.video_streamer.stop()
        if self.tasks:
            self.tasks.cancel()

    def video_start(self, parameters):
        self.logger.info(f'Starting video')

        try:
            host = parameters['host']
            port = parameters['port']
        except KeyError as e:
            self.logger.warning(f'\"Start video\" parameters error: {e}')
            raise ControllerException(f'Error starting video: {e}')

        self.video_streamer.host_set(host, port)
        return f'Video stream to {host}:{port} started'

    def video_stop(self, _):
        self.logger.info(f'Stopping video')
        self.video_streamer.host_remove()
        return 'Video stream stopped'
