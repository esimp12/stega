from __future__ import annotations

import asyncio
import contextlib
import typing as T

import httpx


class AsyncRateLimiter:
    def __init__(self, limit: int = 1, period: int = 1):
        self.limit = limit
        self.period = period
        self.lock = asyncio.Lock()
        self.signal = asyncio.Event()
        self._tasks = [asyncio.create_task(self.tick())]
        self.signal.set()

    async def tick(self):
        while True:
            await asyncio.sleep(self.period / self.limit)
            self.signal.set()

    async def __aenter__(self) -> AsyncRateLimiter:
        async with self.lock:
            await self.signal.wait()
            self.signal.clear()
        return self

    async def __aexit__(self, *args):
        pass


def fetch(
    session: httpx.Client,
    url: str,
):
    return session.get(url)


@contextlib.contextmanager
def acquire_session(
    base_url: str,
    params: dict[str, T.Any] | None = None,
):
    with httpx.Client(
        base_url=base_url,
        params=params,
        http2=True,
    ) as client:
        yield client


async def fetch_async(
    rate: AsyncRateLimiter,
    session: httpx.AsyncClient,
    url: str,
):
    async with rate:
        return await session.get(url)


@contextlib.asynccontextmanager
async def acquire_async_session(
    base_url: str,
    params: dict[str, T.Any] | None = None,
):
    async with httpx.AsyncClient(
        base_url=base_url,
        params=params,
        http2=True,
    ) as client:
        yield client
