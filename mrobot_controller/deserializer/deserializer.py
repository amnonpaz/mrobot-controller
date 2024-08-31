import msgpack
from msgpack import exceptions


class Deserializer:
    def __init__(self):
        pass

    def deserialize(self, serialized_message):
        command, parameters = None, None

        try:
            deserialized_message = msgpack.unpackb(serialized_message)

            if not isinstance(deserialized_message, dict):
                raise ValueError('Received data is not a dictionary')
            if 'command' not in deserialized_message:
                raise KeyError('Missing "command" key in the message')
            if not isinstance(deserialized_message['command'], str):
                raise ValueError('"command" is not a string')

            if 'parameters' not in deserialized_message:
                raise KeyError('Missing "parameters" key')
            if not isinstance(deserialized_message['parameters'], dict):
                raise ValueError('"parameters" is not a dict')

            print(f'OUTPUT {deserialized_message}')

            command = deserialized_message['command']
            parameters = deserialized_message['parameters']
        except exceptions.UnpackException as e:
            print(f'Error during deserialization: {e}')
        except (ValueError, KeyError) as e:
            print(f'Invalid message structure: {e}')

        return command, parameters
