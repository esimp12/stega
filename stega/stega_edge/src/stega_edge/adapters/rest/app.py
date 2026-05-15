from collections.abc import Awaitable

from quart import Quart

from stega_edge.adapters.rest.api import api as edge_portfolio_api
from stega_edge.adapters.rest.sse import api as edge_events_api
from stega_edge.adapters.rest.utils import ResponseType
from stega_edge.bootstrap import service_lifespan
from stega_edge.config import EdgeConfig, create_config, create_logger
from stega_edge.domain.error import (
    AppError,
    ConflictError,
    ResourceNotFoundError,
)


def create_app(config: EdgeConfig) -> Quart:
    app = Quart(__name__)
    StegaQuartApp(config, app)
    register_blueprints(app)
    return app


class StegaQuartApp:
    def __init__(self, config: EdgeConfig, app: Quart | None = None) -> None:
        if app is not None:
            self.init_app(config, app)

    def init_app(self, config: EdgeConfig, app: Quart) -> None:
        app.extensions = getattr(app, "extensions", {})

        @app.while_serving
        async def _manage_service() -> Awaitable[None]:
            async with service_lifespan(config) as lifespan:
                app.extensions["bus"] = lifespan.bus
                app.extensions["service_broker"] = lifespan.service_broker
                app.extensions["client_broker"] = lifespan.client_broker
                try:
                    yield
                finally:
                    app.extensions.pop("bus", None)
                    app.extensions.pop("service_broker", None)
                    app.extensions.pop("client_broker", None)


def register_blueprints(app: Quart) -> None:
    app.register_blueprint(edge_portfolio_api, url_prefix="/api")
    app.register_blueprint(edge_events_api, url_prefix="/api")
    app.register_error_handler(Exception, _api_exception_handler)


def _api_exception_handler(error: Exception) -> ResponseType:
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
    elif isinstance(error, AppError):
        err_msg = str(error)
        logger.warning(err_msg)
        resp = {"msg": err_msg, "ok": False}, 400
    else:
        logger.exception(error)
        resp = {"msg": str(error), "ok": False}, 500
    return resp
