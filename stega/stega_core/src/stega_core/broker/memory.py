import asyncio
from collections.abc import AsyncIterator, Iterable

from stega_core.broker.base import Envelope, MessageBroker


class InMemoryBroker[InT, OutT](MessageBroker[InT, OutT]):
    def __init__(self, queue_maxsize: int = 100) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[Envelope]]] = {}
        self._queue_maxsize = queue_maxsize

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        self._subscribers.clear()

    async def publish(self, envelope: Envelope[OutT]) -> None:
        queues = list(self._subscribers.get(envelope.topic, []))
        for queue in queues:
            try:
                queue.put_nowait(envelope)
            except asyncio.QueueFull:
                pass

    async def subscribe(self, topics: str | Iterable[str]) -> AsyncIterator[Envelope[InT]]:
        queue: asyncio.Queue[Envelope[InT]] = asyncio.Queue(maxsize=self._queue_maxsize)

        topics = [topics] if isinstance(topics, str) else list(topics)
        for topic in topics:
            self._subscribers.setdefault(topic, []).append(queue)

        try:
            while True:
                yield await queue.get()
        finally:
            for topic in topics:
                if topic in self._subscribers:
                    try:
                        self._subscribers[topic].remove(queue)
                    except ValueError:
                        pass
                    if not self._subscribers[topic]:
                        del self._subscribers
