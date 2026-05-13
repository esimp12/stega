from stega_edge.services.handlers.portfolio import (
    create_portfolio,
    delete_portfolio,
    update_portfolio,
)
from stega_contracts.portfolio import (
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
)


COMMAND_HANDLERS = [
    create_portfolio,
    delete_portfolio,
    update_portfolio,
]

QUERY_HANDLERS = []

SERVICE_EVENTS = []
CLIENT_EVENTS = [
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
]
EVENT_HANDLERS = []
