from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TransportMessage:
    topic: str
    body: dict[str, Any]


class MessageTransport(ABC):

    @abstractmethod
    async def publish(self, message: TransportMessage) -> None: ...

    @abstractmethod
    async def subscribe(self, topics: list[str]) -> AsyncIterator[TransportMessage]: ...

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...


PublisherHandler = Callable[[Event, MessageTransport], Awaitable[None]]


def make_publishing_handler(event_type: type[Event]) -> PublisherHandler:
    async def publish(event: event_type, transport: MessageTransport) -> None:
        await transport.publish(
            TransportMessage(
                topic=event.topic,
                body=event.serialize(),
            )
        )
    publish.__name__ = f"publish_{event_type.__name__}"
    return publish
