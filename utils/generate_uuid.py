import uuid


def generate_id() -> uuid.UUID:
    return str(uuid.uuid4())
