from stega_contracts.portfolio.event import (
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
)

from stega_edge.services.handlers.portfolio import (
    create_portfolio,
    delete_portfolio,
    get_portfolio,
    list_portfolio,
    update_portfolio,
)

COMMAND_HANDLERS = [
    create_portfolio,
    delete_portfolio,
    update_portfolio,
]

QUERY_HANDLERS = [
    get_portfolio,
    list_portfolio,
]

SERVICE_EVENTS = []
CLIENT_EVENTS = [
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
]
EVENT_HANDLERS = []
