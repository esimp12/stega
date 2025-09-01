"""Flask app factory for the core service."""

from flask import Flask

# from stega_portfolio.adapters.rest.api import api as portfolio_api
from stega_core.adapters.rest.utils import ResponseType
from stega_core.bootstrap import bootstrap
from stega_core.config import CoreConfig, create_config, create_logger
from stega_core.domain.errors import ConflictError, CoreAppError, ResourceNotFoundError


def create_app(config: CoreConfig) -> Flask:
    """Create a Flask core api app.

    Args:
        config (CoreConfig): Configuration for the core service.

    Returns:
        A Flask application object.

    """
    app = Flask(__name__)
    FlaskCoreApp(config, app)
    register_blueprints(app)
    return app


class FlaskCoreApp:
    """Extension for Flask app to bootstrap MessageBus.

    Attributes:
        app (Flask): Flask app to bootstrap MessageBus with.

    """

    def __init__(
        self,
        config: CoreConfig,
        app: Flask | None = None,
    ) -> None:
        """Initialize FlaskCoreApp extension with current Flask app."""
        if app is not None:
            self.init_app(config, app)

    def init_app(self, config: CoreConfig, app: Flask) -> None:
        """Initialize custom Flask app with appropriate runtime settings.

        Args:
            config (CoreConfig): Configuration for the core service.
            app (Flask): Flask app to bootstrap.

        """
        # app.extensions["bus"] = bootstrap()


def register_blueprints(app: Flask) -> None:
    """Register blueprints with Flask app.

    Args:
        app (Flask): Flask app to register blueprints with.

    """
    # app.register_blueprint(portfolio_api, url_prefix="/api")
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
