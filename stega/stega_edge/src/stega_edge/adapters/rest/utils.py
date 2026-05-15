from quart import current_app
from stega_core import (
    ClientBroker,
    MessageBus,
    ServiceBroker,
)

ResponseType = tuple[dict[str, str | int | bool], int]


def get_service_broker() -> ServiceBroker:
    return current_app.extensions["service_broker"]


def get_client_broker() -> ClientBroker:
    return current_app.extensions["client_broker"]


def get_bus() -> MessageBus:
    return current_app.extensions["bus"]
