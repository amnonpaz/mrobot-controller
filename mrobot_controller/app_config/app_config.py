import json
import logging
import jsonschema


class AppConfig:
    config_schema_file = 'config/config_schema.json'

    def __init__(self, config_file: str):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.schema = None
        self.configuration = None

        self.load_schema()
        self.load_config(config_file)

    def load_schema(self):
        with open(AppConfig.config_schema_file, 'r') as f:
            self.schema = json.load(f)

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            self.configuration = json.load(f)
            jsonschema.validate(self.schema, self.configuration)

            self.log_values()

    def get_video_config(self):
        return self.configuration['video']

    def get_server_config(self):
        return self.configuration['server']

    def get_platform_config(self):
        return self.configuration['platform']

    def log_values(self):
        self.logger.info('Using configuration: ')
        for line in str(self).split('\n'):
            self.logger.info(line)

    def __repr__(self):
        return json.dumps(self.configuration, indent=4)

