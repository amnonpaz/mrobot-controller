import msgpack
from msgpack import exceptions


class DeserializationError(Exception):
    pass


def deserialize(serialized_message):
    try:
        deserialized_message = msgpack.unpackb(serialized_message)

        if not isinstance(deserialized_message, dict):
            raise DeserializationError('Received data is not a dictionary')
        if 'command' not in deserialized_message:
            raise DeserializationError('Missing "command" key in the message')
        if not isinstance(deserialized_message['command'], str):
            raise DeserializationError('"command" is not a string')

        if 'parameters' not in deserialized_message:
            raise DeserializationError('Missing "parameters" key')
        if not isinstance(deserialized_message['parameters'], dict):
            raise DeserializationError('"parameters" is not a dict')

        command = deserialized_message['command']
        parameters = deserialized_message['parameters']
    except exceptions.UnpackException as e:
        raise DeserializationError(f'Error during deserialization: {e}')
    except (ValueError, KeyError) as e:
        raise DeserializationError(f'Invalid message structure: {e}')
    except TypeError as e:
        raise DeserializationError(f'Invalid message type: {e}')

    return command, parameters
