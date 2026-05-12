from __future__ import annotations

from stega_core.message import (
    Message,
    MessageResponse,
    Command,
    CommandResponse,
    Event,
    Query,
    QueryResponse,
    View,
)
from stega_core.di import HandlerBinding
from stega_core.registry.base import (
    FanOutRegistry,
    Registry,
)


class MessageRegistry[MessageT: Message, MessageResponseT: MessageResponse](
    Registry[type[MessageT], HandlerBinding[MessageT, MessageResponseT]]
):
    @property
    def message_types(self) -> set[type[MessageT]]:
        return self.keys


class MessageFanOutRegistry[MessageT: Message, MessageResponseT: MessageResponse](
    FanOutRegistry[type[MessageT], HandlerBinding[MessageT, MessageResponseT]]
):
    @property
    def message_types(self) -> set[type[MessageT]]:
        return self.keys


CommandRegistry = MessageRegistry[Command, CommandResponse]
QueryRegistry = MessageRegistry[Query, QueryResponse[View]]
EventRegistry = MessageFanOutRegistry[Event, None]
