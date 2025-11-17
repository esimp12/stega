"""Entrypoint for the stega core service."""

from __future__ import annotations

import functools
import logging
import multiprocessing
import typing as T

from gunicorn import glogging
from gunicorn.app.base import BaseApplication

from stega_core.adapters.rest.app import create_app
from stega_core.adapters.events.listen import start_listening
from stega_core.config import CoreConfig, create_config, create_logger

if T.TYPE_CHECKING:
    from flask import Flask


class StandaloneApp(BaseApplication):
    """Gunicorn application for the core service."""

    def __init__(self, app: Flask, options: dict[str, T.Any] | None = None) -> None:
        """Initialize the Gunicorn application."""
        self.options = options or {}
        self.app = app
        super().__init__()

    def load_config(self) -> None:
        """Load configuration from the gunicorn config."""
        config = {k: v for k, v in self.options.items() if k in self.cfg.settings and v is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> Flask:
        """Load the Flask application."""
        return self.app


class StubbedGunicornLogger(glogging.Logger):
    """A stubbed logger for Gunicorn that does not log to stderr."""

    def setup(self, _: None) -> None:
        """Set up the logger."""
        config = create_config()
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(config.STEGA_CORE_LOG_LEVEL)
        self.access_logger.setLevel(config.STEGA_CORE_LOG_LEVEL)


def create_core_app(
    ipc_queue: multiprocessing.Queue,
    config: CoreConfig | None = None,
) -> Flask:
    """Create the core service Flask application."""
    if config is None:
        config = create_config()
    logger = create_logger(config, third_party_loggers=["gunicorn.error", "gunicorn.access"])
    logger.info("Starting stega core service...")
    envvars_str = "\n  ".join(f"{k} => {v!r}" for k, v in config.get_envvars())
    envvars_str = "\n  " + envvars_str
    logger.debug("Using following configuration... %s", envvars_str)
    return create_app(ipc_queue)


def run_app(ipc_queue: multiprocessing.Queue) -> None:
    """Run the core app service."""
    config = create_config()
    app = create_core_app(ipc_queue, config)
    if config.STEGA_CORE_GUNICORN:
        options = {
            "bind": f"{config.STEGA_CORE_SERVER_ADDRESS}:{config.STEGA_CORE_SERVER_PORT}",
            "workers": config.STEGA_CORE_GUNICORN_WORKERS,
            "logger_class": StubbedGunicornLogger,
        }
        StandaloneApp(app, options).run()
    else:
        app.run(
            host=config.STEGA_CORE_SERVER_ADDRESS,
            port=config.STEGA_CORE_SERVER_PORT,
            debug=config.STEGA_CORE_DEBUG,
        )


def run_events_consumer(ipc_queue: multiprocessing.Queue) -> None:
    """Run the events listener for the core service."""
    config = create_config()
    start_listening(
        ipc_queue=ipc_queue,
        config=config,
    )


def run() -> None:
    """Run the core service."""
    ipc_queue = multiprocessing.Queue() 
    
    run_app_partial = functools.partial(run_app, ipc_queue=ipc_queue)
    run_events_consumer_partial = functools.partial(run_events_consumer, ipc_queue=ipc_queue)

    app_process = multiprocessing.Process(target=run_app_partial)
    events_process = multiprocessing.Process(target=run_events_consumer_partial)
    processes = (app_process, events_process)
    # start processes
    for process in processes:
        process.start()
    # join processes
    for process in processes:
        process.join()
