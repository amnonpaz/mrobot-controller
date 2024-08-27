import json
import logging


class AppConfig:
    def __init__(self, config_file):
        self.logger = logging.getLogger(__name__)

        # Default values
        self.device = "/dev/video0"
        self.width = 1920
        self.height = 1080

        self.host = "localhost"
        self.port = 5555
        self.test = False

        self.load_config(config_file)

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)

                video_config = config_data.get("video", {})
                server_config = config_data.get("server", {})

                self.device = video_config.get("device", self.device)
                self.width = video_config.get("width", self.width)
                self.height = video_config.get("height", self.height)
                self.test = video_config.get("test", self.test)

                self.host = server_config.get("host", self.host)
                self.port = server_config.get("port", self.port)

                self.log_values()

        except FileNotFoundError:
            self.logger.warning(f"Configuration file {config_file} not found. Using default settings.")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from {config_file}: {e}. Using default settings.")
        except Exception as e:
            self.logger.error(f"An error occurred while loading configuration: {e}. Using default settings.")

    def log_values(self):
        self.logger.info('Using configuration: ')
        for line in str(self).split('\n'):
            self.logger.info(line)

    def __repr__(self):
        return (f'Video:\n    Device: {self.device}\n    Width:  {self.width}\n    Height: {self.height}\n    Test: {self.test}\n'
                f'Server:\n    Host: {self.host}\n    Port: {self.port}')

