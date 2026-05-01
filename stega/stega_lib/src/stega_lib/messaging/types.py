from typing import Protocol

from stega_lib.messaging.command import Command
from stega_lib.messaging.event import Event
from stega_lib.messaging.query import Query
from stega_lib.messaging.response import Response


type ActionType = Command | Query | Event
type NoneType = type(None)
type ResponseType = Response | NoneType


class ActionHandler[TAction: ActionType, TResponse: ResponseType](Protocol):
    async def __call__(self, action: TAction, /, **kwargs: Any) -> TResponse: ...


@dataclass(frozen=True)
class HandlerBinding[TAction: ActionType, TResponse: ResponseType]: 
    handler: ActionHandler[TAction, TResponse]
    action_type: type[TAction]
    dep_types: dict[str, type]
