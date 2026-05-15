from stega_contracts.portfolio import (
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
)

from stega_portfolio.services.handlers.portfolio import (
    create_portfolio,
    delete_portfolio,
    update_portfolio,
)

COMMAND_HANDLERS = [
    create_portfolio,
    delete_portfolio,
    update_portfolio,
]

QUERY_HANDLERS = []

SERVICE_EVENTS = [
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
]
EVENT_HANDLERS = []
