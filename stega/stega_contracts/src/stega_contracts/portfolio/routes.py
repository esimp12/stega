from stega_core import Route

from stega_contracts.portfolio.command import (
    CreatePortfolio,
    UpdatePortfolio,
    DeletePortfolio,
)
from stega_contracts.portfolio.query import (
    GetPortfolio,
    ListPortfolios,
)


ROUTES = [
    # get portfolio
    Route(
        method="GET",
        path="/portfolios/<string:portfolio_id>",
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
    # update portfolio
    Route(
        method="PATCH",
        path="/portfolios/<string:portfolio_id>",
        msg_type=UpdatePortfolio,
        msg_callback=lambda _: "Successfully submitted request to update portfolio.",
        prefix="/api",
        translation={"X-Request-Id": "correlation_id"},
        contextvars={"correlation_id"},
    ),
    # delete portfolio
    Route(
        method="DELETE",
        path="/portfolios/<string:portfolio_id>",
        msg_type=DeletePortfolio,
        msg_callback=lambda _: "Successfully submitted request to delete portfolio.",
        prefix="/api",
        translation={"X-Request-Id": "correlation_id"},
        contextvars={"correlation_id"},
    ),
]
