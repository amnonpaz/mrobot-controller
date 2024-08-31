import msgpack


def serialize(deserialized_message: dict):
    return msgpack.packb(deserialized_message)
