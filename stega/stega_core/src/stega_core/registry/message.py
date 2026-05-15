from __future__ import annotations

from stega_core.di import MessageHandlerBinding
from stega_core.message import (
    Command,
    CommandResponse,
    Event,
    Message,
    MessageResponse,
    Query,
    QueryResponse,
    View,
)
from stega_core.registry.base import (
    FanOutRegistry,
    Registry,
)


class MessageRegistry[MessageT: Message, MessageResponseT: MessageResponse](
    Registry[type[MessageT], MessageHandlerBinding[MessageT, MessageResponseT]]
):
    @property
    def message_types(self) -> set[type[MessageT]]:
        return self.keys


class MessageFanOutRegistry[MessageT: Message, MessageResponseT: MessageResponse](
    FanOutRegistry[type[MessageT], MessageHandlerBinding[MessageT, MessageResponseT]]
):
    @property
    def message_types(self) -> set[type[MessageT]]:
        return self.keys


CommandRegistry = MessageRegistry[Command, CommandResponse]
QueryRegistry = MessageRegistry[Query, QueryResponse[View]]
EventRegistry = MessageFanOutRegistry[Event, None]
