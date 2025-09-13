"""Flask app factory for the portfolio service."""

from flask import Flask
from sqlalchemy.orm import sessionmaker

from stega_portfolio.adapters.rest.api import api as portfolio_api
from stega_portfolio.adapters.rest.health import api as health_api
from stega_portfolio.adapters.rest.utils import ResponseType
from stega_portfolio.bootstrap import bootstrap
from stega_portfolio.config import PortfolioConfig, create_config, create_logger
from stega_portfolio.domain.errors import ConflictError, PortfolioAppError, ResourceNotFoundError
from stega_portfolio.ports.orm import get_engine
from stega_portfolio.services.uow.db import SqlAlchemyUnitOfWork


def create_app(config: PortfolioConfig) -> Flask:
    """Create a Flask portfolio api app.

    Args:
        config (PortfolioConfig): Configuration for the portfolio service.

    Returns:
        A Flask application object.

    """
    app = Flask(__name__)
    FlaskPortfolioApp(config, app)
    register_blueprints(app)
    return app


class FlaskPortfolioApp:
    """Extension for Flask app to bootstrap MessageBus.

    Attributes:
        app (Flask): Flask app to bootstrap MessageBus with.

    """

    def __init__(
        self,
        config: PortfolioConfig,
        app: Flask | None = None,
    ) -> None:
        """Initialize FlaskPortfolioApp extension with current Flask app."""
        if app is not None:
            self.init_app(config, app)

    def init_app(self, config: PortfolioConfig, app: Flask) -> None:
        """Initialize custom Flask app with appropriate runtime settings.

        Args:
            config (PortfolioConfig): Configuration for the portfolio service.
            app (Flask): Flask app to bootstrap.

        """
        default_session_factory = sessionmaker(
            bind=get_engine(config.db_uri),
            expire_on_commit=False,
        )
        app.extensions["bus"] = bootstrap(
            uow=SqlAlchemyUnitOfWork(default_session_factory),
        )


def register_blueprints(app: Flask) -> None:
    """Register blueprints with Flask app.

    Args:
        app (Flask): Flask app to register blueprints with.

    """
    app.register_blueprint(health_api, url_prefix="/api")
    app.register_blueprint(portfolio_api, url_prefix="/api")
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
    elif isinstance(error, PortfolioAppError):
        err_msg = str(error)
        logger.warning(err_msg)
        resp = {"msg": err_msg, "ok": False}, 400
    else:
        logger.exception(error)
        resp = {"msg": str(error), "ok": False}, 500
    return resp
