from stega_core import Binding, Origin, Route, Wire

from stega_contracts.portfolio.command import (
    CreatePortfolio,
    DeletePortfolio,
    UpdatePortfolio,
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
        bindings=[
            Binding(key="correlation_id", wire=Wire.HEADER, origin=Origin.CONTEXT, wire_key="X-Request-Id"),
        ],
    ),
    # update portfolio
    Route(
        method="PATCH",
        path="/portfolios/<string:portfolio_id>",
        msg_type=UpdatePortfolio,
        msg_callback=lambda _: "Successfully submitted request to update portfolio.",
        prefix="/api",
        bindings=[
            Binding(key="correlation_id", wire=Wire.HEADER, origin=Origin.CONTEXT, wire_key="X-Request-Id"),
        ],
    ),
    # delete portfolio
    Route(
        method="DELETE",
        path="/portfolios/<string:portfolio_id>",
        msg_type=DeletePortfolio,
        msg_callback=lambda _: "Successfully submitted request to delete portfolio.",
        prefix="/api",
        bindings=[
            Binding(key="correlation_id", wire=Wire.HEADER, origin=Origin.CONTEXT, wire_key="X-Request-Id"),
        ],
    ),
]
