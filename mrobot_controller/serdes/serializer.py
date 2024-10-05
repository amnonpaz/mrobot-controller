import msgpack


def serialize(deserialized_message: dict) -> bytes | None:
    return msgpack.packb(deserialized_message)
