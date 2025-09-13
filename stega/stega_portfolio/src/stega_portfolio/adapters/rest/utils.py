"""Flask app utilities for the stega portfolio service."""

from flask import current_app

from stega_portfolio.views.views import View
from stega_portfolio.services.messagebus import MessageBus

Response = dict[str, str | int | bool]
ViewResponse = dict[str, str | bool | View | list[View]]
ResponseType = tuple[Response, int]
ViewResponseType = tuple[ViewResponse, int]


def get_bus() -> MessageBus:
    """Get the current application MessageBus.

    Returns:
        A MessageBus instance.

    """
    return current_app.extensions["bus"]
