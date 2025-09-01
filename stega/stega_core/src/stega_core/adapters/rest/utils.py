"""Flask app utilities for the stega core service."""

from flask import current_app

from stega_core.bootstrap import Dispatcher

ResponseType = tuple[dict[str, str | int | bool], int]


def get_dispatcher() -> Dispatcher:
    """Get the current application service Dispatcher.

    Returns:
        A service handler Dispatcher.

    """
    return current_app.extensions["dispatcher"]
