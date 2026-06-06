import asyncio
import logging

from stega_core import (
    Route,
    build_quart_app,
    init_logger,
    serve_hypercorn,
    RepositoryRuntime,
)

from stega_portfolio.ports.orm import start_mappers, init_metadata
from stega_portfolio.bootstrap import build_service, get_db_uri
from stega_portfolio.config import create_config
from stega_portfolio.domain.command import (
    CreatePortfolio,
)
from stega_portfolio.domain.query import (
    GetPortfolio,
    ListPortfolios,
)


def routes() -> list[Route]:
    return [
        # get portfolio
        Route(
            method="GET",
            path="/portfolio/<string:portfolio_id>",
            msg_type=GetPortfolio,
            msg_callback=lambda _: "Successfully fetched portfolio.",
            prefix="/api",
        ),
        # list portfolios
        Route(
            method="GET",
            path="/portfolios",
            msg_type=ListPortfolios,
            msg_callback=lambda _: "Successfully fetched all portfolios.",
            prefix="/api",
        ),
        # create portfolio
        Route(
            method="POST",
            path="/portfolios",
            msg_type=CreatePortfolio,
            msg_callback=lambda _: "Successfully submitted request to create portfolio.",
            prefix="/api",
            translation={"X-Request-Id": "correlation_id"},
            contextvars={"correlation_id"},
        ),
    ]


def run_rest_app() -> None:
    # setup config and logger
    config = create_config()
    init_logger(
        service_name="stega_portfolio",
        log_level=config.LOG_LEVEL,
        third_party_logger_names=["hypercorn"],
    )
    logger = logging.getLogger(__name__)

    # build service and app
    service = build_service(config)
    app = build_quart_app(service, routes())

    # start mappers if persisted runtime
    is_sqlalchemy = RepositoryRuntime.SQLITE | RepositoryRuntime.POSTGRES
    if bool(config.REPOSITORY_RUNTIME & is_sqlalchemy):
        logger.info("Initializing metadata & starting mappers...")
        db_uri = get_db_uri(config, is_async=False)
        init_metadata(db_uri)
        start_mappers()

    asyncio.run(
        serve_hypercorn(
            app=app,
            log_level=config.LOG_LEVEL,
            host=config.HOST,
            port=config.PORT,
        )
    )
