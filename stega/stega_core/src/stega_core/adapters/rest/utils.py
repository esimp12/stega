"""Flask app utilities for the stega core service."""

from flask import current_app

from stega_core.bootstrap import Dispatcher
from stega_core.services.handlers.streams import ClientStreams
from stega_core.services.messagebus import MessageBus

ResponseType = tuple[dict[str, str | int | bool], int]


def get_dispatcher() -> Dispatcher:
    """Get the current application service Dispatcher.

    Returns:
        A service handler Dispatcher.

    """
    return current_app.extensions["dispatcher"]


def get_event_bus() -> MessageBus: 
    """Get the current application MessageBus. 

    Returns:
        A MessageBus instance. 

    """
    return current_app.extensions["bus"]


def get_client_streams() -> ClientStreams: 
    """Get the current application client topic fan-out queues. 

    Returns:
        A ClientStreams instance. 

    """
    return current_app.extensions["streams"]

