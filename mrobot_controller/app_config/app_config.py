import json
import logging


class AppConfig:
    def __init__(self, config_file: str):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = {
            'video': {
                'device': "/dev/video0",
                'width': 640,
                'height': 480,
                'test': False
            },
            'app-server': {
                'port': 8765
            }
        }

        self.load_config(config_file)

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)

                video_config = config_data.get("video", {})
                server_config = config_data.get("app-server", {})

                self.config['video']['device'] = video_config.get("device", self.config['video']['device'])
                self.config['video']['width'] = video_config.get("width", self.config['video']['width'])
                self.config['video']['height'] = video_config.get("height", self.config['video']['height'])
                self.config['video']['test'] = video_config.get("test", self.config['video']['test'])

                self.config['app-server']['port'] = server_config.get("port", self.config['app-server']['port'])

                self.log_values()

        except FileNotFoundError:
            self.logger.warning(f"Configuration file {config_file} not found. Using default settings.")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from {config_file}: {e}. Using default settings.")
        except Exception as e:
            self.logger.error(f"An error occurred while loading configuration: {e}. Using default settings.")

    def get_video_config(self):
        return self.config['video']

    def get_app_server_config(self):
        return self.config['app-server']

    def log_values(self):
        self.logger.info('Using configuration: ')
        for line in str(self).split('\n'):
            self.logger.info(line)

    def __repr__(self):
        return (f'Video:\n'
                f'    Device: {self.config['video']['device']}\n'
                f'    Width:  {self.config['video']['width']}\n'
                f'    Height: {self.config['video']['height']}\n'
                f'    Test: {self.config['video']['test']}\n'
                f'Server:\n'
                f'    Port: {self.config['app-server']['port']}')

