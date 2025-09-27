"""Service handler mapping for stega_portfolio."""

import typing as T

from stega_lib.domain import Command
from stega_lib.events import Event, PortfolioCreated, PortfolioDeleted, PortfolioUpdated

from stega_portfolio.domain.commands import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_portfolio.services.handlers.portfolio import (
    create_portfolio,
    delete_portfolio,
    update_portfolio,
)
from stega_portfolio.services.uow.base import AbstractUnitOfWork

CommandType = type[Command]
EventType = type[Event]


def _publish_external_event(event: Event, publish: T.Callable) -> None:
    publish(event)


COMMAND_HANDLERS: dict[CommandType, T.Callable[[Command, AbstractUnitOfWork], None]] = {
    CreatePortfolio: create_portfolio,
    DeletePortfolio: delete_portfolio,
    UpdatePortfolio: update_portfolio,
}

EVENT_HANDLERS: dict[EventType, list[T.Callable]] = {
    PortfolioCreated: [_publish_external_event],
    PortfolioDeleted: [_publish_external_event],
    PortfolioUpdated: [_publish_external_event],
}

INTERNAL_EVENTS: list[EventType] = [
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
]
