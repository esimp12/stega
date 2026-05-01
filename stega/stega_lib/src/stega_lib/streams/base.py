from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any 


@dataclass(frozen=True)
class StreamMessage:
    channel: str
    payload: dict[str, Any]


class AsyncSubscription(ABC):

    @abstractmethod
    async def __aiter__(self) -> AsyncIterator[StreamMessage]: ...

    @abstractmethod
    async def close(self) -> None: ...


class StreamBroker(ABC):

    @abstractmethod
    async def publish(self, msg: StreamMessage) -> None: ...

    @abstractmethod
    async def subscribe(self, channel: str) -> AsyncSubscription: ...

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass


StreamBroadcasterHandler = Callable[Event, StreamBroker], Awaitable[None]]


def make_stream_broadcaster(event_type: type[Event], channel: str | None = None) -> StreamBroadcasterHandler:
    async def broadcast(event: event_type, broker: StreamBroker) -> None:
        await broker.publish(
            StreamMessage(
                channel=channel or event.topic,
                payload=event.serialize(),
            )
        )
    broadcast.__name__ = f"broadcast_{event_type.__name__}"
    return broadcast
