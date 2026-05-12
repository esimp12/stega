from stega_core.command import Command
from stega_core.event import Event
from stega_core.query import Query
from stega_core.registry.base import FanOutRegistry, Registry
from stega_core.response import (
    CommandResponse,
    QueryResponse,
)
from stega_core.view import View

CommandRegistry = Registry[Command, CommandResponse]
QueryRegistry = Registry[Query, QueryResponse[View]]
EventRegistry = FanOutRegistry[Event, None]
