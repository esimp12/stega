import asyncio

from stega_core import HypercornRuntimeFields, Route, build_quart_app, init_logger, serve_hypercorn

from stega_portfolio.bootstrap import build_service
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
        ),
    ]


def run_rest_app() -> None:
    config = create_config()
    init_logger(
        service_name="stega_portfolio",
        log_level=config.STEGA_PORTFOLIO_LOG_LEVEL,
        third_party_logger_names=["hypercorn"],
    )
    service = build_service(config)
    app = build_quart_app(service, routes())
    runtime_fields = HypercornRuntimeFields()
    asyncio.run(
        serve_hypercorn(
            app=app,
            config=config,
            runtime_fields=runtime_fields,
        )
    )
