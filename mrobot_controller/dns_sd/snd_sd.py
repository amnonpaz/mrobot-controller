import socket
import netifaces
from zeroconf import ServiceInfo, Zeroconf
import logging


class ServicePublisher:

    def __init__(self, service_name: str, port: int):
        self.logger = logging.getLogger(f'{self.__class__.__name__}-{service_name}')
        self.zeroconf = Zeroconf()
        self.service_name = f'_{service_name}._websocket._tcp.local.'
        self.port = port

        all_ips = [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for iface in netifaces.interfaces() if netifaces.AF_INET in netifaces.ifaddresses(iface)]
        self.local_ips = list(filter(lambda s: not s.startswith('127') and not s.startswith('172'), all_ips))

        self.info = ServiceInfo(
            '_websocket._tcp.local.',
            name=self.service_name,
            addresses=self.local_ips, # socket.inet_aton(self.local_ips),
            port=port,
            properties={'path': '/ws'},
            server="websocket-server.local."
        )

    def get_ips(self):
        return self.local_ips

    def publish(self):
        self.zeroconf.register_service(self.info)
        self.logger.info(f"WebSocket service '{self.service_name}' published on {self.info.parsed_addresses()}")

    def unpublish(self):
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()
        self.logger.info(f"WebSocket service '{self.service_name}' removed")
