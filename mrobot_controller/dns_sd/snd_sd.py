import socket
from zeroconf import ServiceInfo, Zeroconf
import logging


class ServicePublisher:

    def __init__(self, service_name: str, port: int):
        self.logger = logging.getLogger(f'{self.__class__.__name__}-{service_name}')
        self.zeroconf = Zeroconf()
        self.service_name = f'_{service_name}._websocket._tcp.local.'
        self.port = port

        local_ip = socket.gethostbyname(socket.gethostname())

        self.info = ServiceInfo(
            '_websocket._tcp.local.',
            name=self.service_name,
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties={'path': '/ws'},
            server="websocket-server.local."
        )

    def publish(self):
        self.zeroconf.register_service(self.info)
        self.logger.info(f"WebSocket service '{self.service_name}' published on port {self.port}")

    def unpublish(self):
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()
        self.logger.info(f"WebSocket service '{self.service_name}' removed")
