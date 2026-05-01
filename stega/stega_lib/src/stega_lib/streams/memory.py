import asyncio
from collections.abc import AsyncIterator
from typing import Callable, Awaitable

from stega_lib.streams.base import AsyncSubscription, StreamMessage, StreamBroker


class InMemoryAsyncSubscription(AsyncSubscription):

    def __init__(
        self,
        queue: asyncio.Queue[StreamMessage],
        on_close: Callable[[], Awaitable[None]],
    ) -> None:
        self._queue = queue
        self._closed = False
        self._on_close = on_close

    async def __aiter__(self) -> AsyncIterator[StreamMessage]:
        while not self._closed:
            try:
                msg = await self._queue.get()
                yield msg
            except asyncio.CancelledError:
                break

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self._on_close()


class InMemoryStreamBroker(StreamBroker):

    def __init__(self, queue_maxsize: int = 100) -> None:
        self._channels = dict[str, list[asyncio.Queue[StreamMessage]]] = {}
        self._queue_maxsize = queue_maxsize
    
    async def publish(self, msg: StreamMessage) -> None:
        queues = list(self._channels.get(msg.channel, []))
        for queue in queues:
            try:
                queue.put_nowait(msg)
            except asyncio.QueueFull:
                pass

    async def subscribe(self, channel: str) -> AsyncSubscription:
        queue: asyncio.Queue[StreamMessage] = asyncio.Queue(maxsize=self._queue_maxsize)
        self._channels.setdefault(channel, []).append(queue)

        async def on_close() -> None:
            if channel in self._channels:
                try:
                    self._channels[channel].remove(queue)
                except ValueError:
                    pass
                if not self._channels[channel]:
                    del self._channels[channel]

        return InMemoryAsyncSubscription(queue=queue, on_close=on_close)
