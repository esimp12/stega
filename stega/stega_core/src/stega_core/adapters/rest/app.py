"""Flask app factory for the core service."""

import typing as T

from flask import Flask

from stega_core.adapters.rest.api import api as core_portfolio_api
from stega_core.adapters.rest.sse import api as core_events_api
from stega_core.adapters.rest.utils import ResponseType
from stega_core.bootstrap import bootstrap_dispatcher
from stega_core.config import create_config, create_logger
from stega_core.domain.errors import ConflictError, CoreAppError, ResourceNotFoundError
from stega_core.ports.http import HttpRestPortfolioServicePort

if T.TYPE_CHECKING:
    from stega_core.ports.base import ServiceType


def create_app() -> Flask:
    """Create a Flask core api app.

    Returns:
        A Flask application object.

    """
    app = Flask(__name__)
    FlaskCoreApp(app)
    register_blueprints(app)
    return app


class FlaskCoreApp:
    """Extension for Flask app to bootstrap MessageBus.

    Attributes:
        app (Flask): Flask app to bootstrap MessageBus with.

    """

    def __init__(
        self,
        app: Flask | None = None,
    ) -> None:
        """Initialize FlaskCoreApp extension with current Flask app."""
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize custom Flask app with appropriate runtime settings.

        Args:
            app (Flask): Flask app to bootstrap.

        """
        services: list[ServiceType] = [
            HttpRestPortfolioServicePort(),
        ]
        app.extensions["dispatcher"] = bootstrap_dispatcher(services)


def register_blueprints(app: Flask) -> None:
    """Register blueprints with Flask app.

    Args:
        app (Flask): Flask app to register blueprints with.

    """
    app.register_blueprint(core_portfolio_api, url_prefix="/api")
    app.register_blueprint(core_events_api, url_prefix="/api")
    app.register_error_handler(Exception, _api_exception_handler)


def _api_exception_handler(error: Exception) -> ResponseType:
    """Handle exceptions raised by the API."""
    config = create_config()
    logger = create_logger(config)

    if isinstance(error, ConflictError):
        err_msg = str(error)
        logger.warning(err_msg)
        resp = {"msg": err_msg, "ok": False}, 409
    elif isinstance(error, ResourceNotFoundError):
        err_msg = str(error)
        logger.warning(err_msg)
        resp = {"msg": err_msg, "ok": False}, 404
    elif isinstance(error, CoreAppError):
        err_msg = str(error)
        logger.warning(err_msg)
        resp = {"msg": err_msg, "ok": False}, 400
    else:
        logger.exception(error)
        resp = {"msg": str(error), "ok": False}, 500
    return resp
