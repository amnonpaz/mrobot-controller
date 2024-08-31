import msgpack
from msgpack import exceptions


class Deserializer:
    def __init__(self):
        pass

    def deserialize(self, serialized_message):
        command, parameters = None, None

        try:
            received_message = msgpack.unpackb(serialized_message)

            if not isinstance(received_message, dict):
                raise ValueError('Received data is not a dictionary')
            if 'command' not in received_message:
                raise KeyError('Missing "command" key in the message')
            if not isinstance(received_message['command'], str):
                raise ValueError('"command" is not a string')

            if 'parameters' not in received_message:
                raise KeyError('Missing "parameters" key')
            if not isinstance(received_message['parameters'], dict):
                raise ValueError('"parameters" is not a dict')

            command = received_message['command']
            parameters = received_message['parameters']
        except exceptions.UnpackException as e:
            print(f'Error during deserialization: {e}')
        except (ValueError, KeyError) as e:
            print(f'Invalid message structure: {e}')

        return command, parameters
