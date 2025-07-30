"""Service handler mapping for stega_portfolio."""

import typing as T

from stega_lib.domain import Command
from stega_lib.events import Event

from stega_portfolio.domain.commands import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_portfolio.services.handlers.portfolio import create_portfolio, delete_portfolio, update_portfolio
from stega_portfolio.services.uow.base import AbstractUnitOfWork

CommandType = type[Command]
EventType = type[Event]


COMMAND_HANDLERS: dict[CommandType, T.Callable[[Command, AbstractUnitOfWork], None]] = {
    CreatePortfolio: create_portfolio,
    DeletePortfolio: delete_portfolio,
    UpdatePortfolio: update_portfolio,
}

EVENT_HANDLERS: dict[EventType, T.Callable[[Event, AbstractUnitOfWork], None]] = {
    # Define your event handlers here
}
