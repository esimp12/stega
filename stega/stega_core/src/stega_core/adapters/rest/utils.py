"""Flask app utilities for the stega core service."""

from flask import current_app

from stega_core.bootstrap import Dispatcher
from stega_core.services.handlers.streams import ClientStreams

ResponseType = tuple[dict[str, str | int | bool], int]


def get_dispatcher() -> Dispatcher:
    """Get the current application service Dispatcher.

    Returns:
        A service handler Dispatcher.

    """
    return current_app.extensions["dispatcher"]


def get_client_streams() -> ClientStreams: 
    """Get the current application client topic fan-out queues.

    Returns:
        A ClientStreams instance. 

    """
    return current_app.extensions["streams"]

