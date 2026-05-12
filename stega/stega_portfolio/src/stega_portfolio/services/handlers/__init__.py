from stega_portfolio.services.handlers.portfolio import (
    create_portfolio,
    delete_portfolio,
    update_portfolio,
)
from stega_lib.messaging.events import (
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

PUBLISHED_EVENTS = [
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
]
