"""Flask app utilities for the stega portfolio service."""

from flask import current_app

from stega_portfolio.services.messagebus import MessageBus

ResponseType = tuple[dict[str, str | int | bool], int]


def get_bus() -> MessageBus:
    """Get the current application MessageBus.

    Returns:
        A MessageBus instance.

    """
    return current_app.extensions["bus"]
