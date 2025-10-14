"""Service handler mapping for stega core service."""

import typing as T

from stega_lib.domain import Command, CommandType
from stega_lib.events import Event, EventType

from stega_core.domain.commands import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_core.ports.base import ServiceType
from stega_core.services.handlers.portfolio import create_portfolio, delete_portfolio, update_portfolio

PrimitiveType = str | None

CommandHandlerType = T.Callable[[Command, ServiceType], PrimitiveType]
CommandHandlerMappingType = dict[CommandType, CommandHandlerType]

EventHandlerType = T.Callable[[Event], None]
EventHandlerMappingType = dict[EventType, EventHandlerType]

COMMAND_HANDLERS: CommandHandlerMappingType = {
    CreatePortfolio: create_portfolio,
    DeletePortfolio: delete_portfolio,
    UpdatePortfolio: update_portfolio,
}

EVENT_HANDLERS: EventHandlerMappingType = {}
