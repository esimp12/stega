from stega_core.message.command import Command
from stega_core.message.event import (
    Event,
    EventDispatch,
)
from stega_core.message.query import Query
from stega_core.message.response import (
    QueryStatus,
    SubmissionStatus,
    Response,
    CommandResponse,
    QueryResponse,
)
from stega_core.message.view import View


type Message = Command | Event | Query
type MessageResponse = Response | None


__all__ = [
    "Message",
    "Response",
    "Command",
    "Event",
    "EventDispatch",
    "Query",
    "QueryStatus",
    "SubmissionStatus",
    "Response",
    "CommandResponse",
    "QueryResponse",
    "View",
]
