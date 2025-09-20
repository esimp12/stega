"""Service handler mapping for stega_portfolio."""

import typing as T

from stega_lib.domain import Command
from stega_lib.events import Event, PortfolioCreated, PortfolioDeleted, PortfolioUpdated

from stega_portfolio.domain.commands import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_portfolio.services.handlers.portfolio import (
    create_portfolio,
    delete_portfolio,
    update_portfolio,
    portfolio_created,
    portfolio_deleted,
    portfolio_updated,
)
from stega_portfolio.services.uow.base import AbstractUnitOfWork

CommandType = type[Command]
EventType = type[Event]


COMMAND_HANDLERS: dict[CommandType, T.Callable[[Command, AbstractUnitOfWork], None]] = {
    CreatePortfolio: create_portfolio,
    DeletePortfolio: delete_portfolio,
    UpdatePortfolio: update_portfolio,
}

EVENT_HANDLERS: dict[EventType, T.Callable[[Event, AbstractUnitOfWork], None]] = {
    PortfolioCreated: portfolio_created,
    PortfolioDeleted: portfolio_deleted,
    PortfolioUpdated: portfolio_updated,
}
