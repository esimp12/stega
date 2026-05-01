from stega_lib.core.command import Command
from stega_lib.core.event import Event
from stega_lib.core.query import Query
from stega_lib.core.response import (
    CommandResponse,
    QueryResponse,
)
from stega_lib.core.view import View
from stega_lib.registry import Registry, FanOutRegistry


CommandRegistry = Registry[Command, CommandResponse]
QueryRegistry = Registry[Query, QueryResponse[View]]
EventRegistry = FanOutRegistry[Event, None]
