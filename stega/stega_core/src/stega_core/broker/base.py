from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import Any

from stega_core.message import Event


@dataclass(frozen=True, kw_only=True)
class Envelope[PayloadT]:
    topic: str
    payload: PayloadT 


class MessageBroker[InT, OutT](ABC):

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def publish(self, envelope: Envelope[OutT]) -> None: ...

    @abstractmethod
    async def subscribe(self, topics: str | Iterable[str]) -> AsyncIterator[Envelope[InT]]: ...


class ServiceBroker[InT, OutT](MessageBroker[InT, OutT]):
    pass


class ClientBroker[InT, OutT](MessageBroker[InT, OutT]):
    pass


type ServicePublishHandler = Callable[
    [Event, ServiceBroker],
    Awaitable[None],
]


type ClientPublishHandler = Callable[
    [Event, ClientBroker],
    Awaitable[None],
]


def make_service_publish_handler(event_type: type[Event]) -> ServicePublishHandler:
    async def publish(event: event_type, broker: ServiceBroker) -> None:
        await broker.publish(
            Envelope(
                topic=event.topic,
                payload=event.serialize(),
            )
        )
    publish.__name__ = f"publish_service_{event_type.__name__}"
    return publish


def make_client_publish_handler(event_type: type[Event]) -> ClientPublishHandler:
    async def publish(event: event_type, broker: ClientBroker) -> None:
        await broker.publish(
            Envelope(
                topic=event.topic,
                payload=event.serialize(),
            )
        )
    publish.__name__ = f"publish_client_{event_type.__name__}"
    return publish
