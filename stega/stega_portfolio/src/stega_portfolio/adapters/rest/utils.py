from quart import current_app
from stega_core import MessageBus

ResponseType = tuple[dict[str, str | int | bool], int]


def get_bus() -> MessageBus:
    return current_app.extensions["bus"]
