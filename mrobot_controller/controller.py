import asyncio
import base64
import logging
import io
from PIL import Image
from .websocket import WebSocketServer, WebSocketMessageHandler
from .serdes import deserialize, DeserializationError, serialize
from .video_streamer import VideoStreamer, VideoFrameHandler
from .dns_sd import ServicePublisher, get_all_ips


class ControllerException(Exception):
    pass


class Controller(WebSocketMessageHandler, VideoFrameHandler):
    def __init__(self, port: int, video_config: dict):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.service_publisher = ServicePublisher('mrobot-server', port)
        self.websocket_server = WebSocketServer(self, hosts=get_all_ips(), port=port)
        self.video_streamer = VideoStreamer(self,
                                            video_config['device'],
                                            video_config['width'],
                                            video_config['height'],
                                            video_config['test'])
        self.event_loop = None
        self.tasks = None

        self.commands = {
            'video_start': self.video_start,
            'video_stop': self.video_stop
        }

    def handle_message(self, message):
        success = False
        command = 'unknown'
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
        except Exception as e:
            self.logger.warning(f'Unknown error: {e}')
            response = str(e)

        return serialize({'command': command, 'success': success, 'response': response})

    async def on_client_disconnection(self):
        self.logger.info(f'Client disconnected, stopping video')
        self.video_streamer.pause()

    def handle_frame(self, raw_data, _):
        self.logger.debug('Sending frame')

        image = Image.frombytes("RGB", (640, 480), raw_data)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        serialized_message = serialize({'event': 'video_frame', 'payload': img_base64})
        asyncio.run_coroutine_threadsafe(self.websocket_server.send(serialized_message), self.event_loop)

    async def run(self) -> None:
        self.logger.info('Starting server')

        self.service_publisher.publish()

        self.event_loop = asyncio.get_running_loop()
        self.tasks = await asyncio.gather(
            asyncio.to_thread(self.video_streamer.start),
            asyncio.create_task(self.websocket_server.start())
        )

    def stop(self) -> None:
        if self.service_publisher:
            self.service_publisher.unpublish()
        if self.video_streamer:
            self.video_streamer.stop()
        if self.tasks:
            self.tasks.cancel()

    def video_start(self, _) -> str:
        self.logger.info(f'Starting video')
        self.video_streamer.play()
        return f'video started'

    def video_stop(self, _) -> str:
        self.logger.info(f'Stopping video')
        self.video_streamer.pause()
        return 'video stopped'
