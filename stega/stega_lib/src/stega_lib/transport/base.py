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
