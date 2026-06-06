from stega_core.message.command import Command
from stega_core.message.event import (
    Event,
    EventDispatch,
    classproperty,
    get_correlation_id,
)
from stega_core.message.query import Query
from stega_core.message.response import (
    CommandResponse,
    QueryResponse,
    QueryStatus,
    Response,
    SubmissionStatus,
)
from stega_core.message.view import View

type Message = Command | Event | Query
type MessageResponse = Response | None


__all__ = [
    "Command",
    "CommandResponse",
    "Event",
    "EventDispatch",
    "Message",
    "Query",
    "QueryResponse",
    "QueryStatus",
    "Response",
    "Response",
    "SubmissionStatus",
    "View",
    "classproperty",
    "get_correlation_id",
]
