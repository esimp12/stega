"""Flask app utilities for the stega core service."""

import multiprocessing

from flask import current_app

from stega_core.bootstrap import Dispatcher

ResponseType = tuple[dict[str, str | int | bool], int]


def get_dispatcher() -> Dispatcher:
    """Get the current application service Dispatcher.

    Returns:
        A service handler Dispatcher.

    """
    return current_app.extensions["dispatcher"]


def get_ipc_queue() -> multiprocessing.Queue:
    """Get the current application IPC multiprocessing queue.

    Returns:
        A multiprocessing Queue.

    """
    return current_app.extensions["ipc_queue"]

