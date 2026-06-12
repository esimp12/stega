import asyncio

from stega_contracts.portfolio.routes import ROUTES as PORTFOLIO_ROUTES
from stega_core import (
    SseRoute,
    build_quart_app,
    init_logger,
    serve_hypercorn,
)

from stega_edge.bootstrap import build_service
from stega_edge.config import create_config

ROUTES = [
    PORTFOLIO_ROUTES,
]

SSE_ROUTES = [
    SseRoute(
        path="/events/<string:topic>",
        prefix="/api",
    ),
]


def run_rest_app() -> None:
    # setup config and logger
    config = create_config()
    init_logger(
        service_name="stega_edge",
        log_leve=config.LOG_LEVEL,
        third_party_logger_names=["hypercorn"],
    )

    # build service and app
    service = build_service(config)
    app = build_quart_app(service, ROUTES, SSE_ROUTES)

    asyncio.run(
        serve_hypercorn(
            app=app,
            log_level=config.LOG_LEVEL,
            host=config.HOST,
            port=config.PORT,
        )
    )
