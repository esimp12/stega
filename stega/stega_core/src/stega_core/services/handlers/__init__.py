from stega_core.services.handlers.portfolio import create_portfolio, delete_portfolio, update_portfolio
from stega_lib.messaging.events import PortfolioCreated, PortfolioDeleted, PortfolioUpdated 


COMMAND_HANDLERS = [
    create_portfolio,
    delete_portfolio,
    update_portfolio,
]

QUERY_HANDLERS = []

STREAMED_EVENTS = [
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
]
EVENT_HANDLERS = []
