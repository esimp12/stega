"""Service handler mapping for stega core service."""

import multiprocessing
import typing as T

from stega_lib.domain import Command, CommandType
from stega_lib.events import Event, EventType, PortfolioCreated, PortfolioDeleted, PortfolioUpdated

from stega_core.domain.commands import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_core.ports.base import ServiceType
from stega_core.services.handlers.portfolio import create_portfolio, delete_portfolio, update_portfolio
from stega_core.services.handlers.events import enqueue_streamed_event
from stega_core.services.handlers.streams import ClientStreams

PrimitiveType = str | None

CommandHandlerType = T.Callable[[Command, ServiceType], PrimitiveType]
CommandHandlerMappingType = dict[CommandType, CommandHandlerType]

EventHandlerType = T.Callable[[Event, ClientStreams], None]
EventHandlerMappingType = dict[EventType, EventHandlerType]

COMMAND_HANDLERS: CommandHandlerMappingType = {
    CreatePortfolio: create_portfolio,
    DeletePortfolio: delete_portfolio,
    UpdatePortfolio: update_portfolio,
}

EVENT_HANDLERS: EventHandlerMappingType = {
    PortfolioCreated: enqueue_streamed_event,
    PortfolioDeleted: enqueue_streamed_event,
    PortfolioUpdated: enqueue_streamed_event,
}
