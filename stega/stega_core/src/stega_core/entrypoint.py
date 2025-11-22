"""Entrypoint for the stega core service."""

from __future__ import annotations

import functools
import logging
import threading
import typing as T

from gunicorn import glogging
from gunicorn.app.base import BaseApplication

from stega_core.adapters.rest.app import create_app
from stega_core.adapters.events.listen import start_listening
from stega_core.services.handlers.streams import ClientStreams
from stega_core.bootstrap import bootstrap_event_bus
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
    return create_app()


def run_app() -> None:
    """Run the core app service."""
    config = create_config()
    app = create_core_app(config)
    
    # Post fork callback to run in each gunicorn worker
    def post_fork(server, worker):
        streams = ClientStreams()
        worker_app = worker.app.app
        worker_app.extensions["streams"] = streams
        events_thread = threading.Thread(target=run_events_consumer, args=(streams,), daemon=True)
        events_thread.start()

    if config.STEGA_CORE_GUNICORN:
        options = {
            "bind": f"{config.STEGA_CORE_SERVER_ADDRESS}:{config.STEGA_CORE_SERVER_PORT}",
            "workers": config.STEGA_CORE_GUNICORN_WORKERS,
            "logger_class": StubbedGunicornLogger,
            "post_fork": post_fork, 
        }
        StandaloneApp(app, options).run()
    else:
        app.run(
            host=config.STEGA_CORE_SERVER_ADDRESS,
            port=config.STEGA_CORE_SERVER_PORT,
            debug=config.STEGA_CORE_DEBUG,
        )


def run_events_consumer(streams: ClientStreams) -> None:
    """Run the events listener for the core service."""
    config = create_config()
    bus = bootstrap_event_bus(streams)
    start_listening(
        config=config,
        bus=bus, 
    )


def run() -> None:
    # Start flask app
    run_app()

