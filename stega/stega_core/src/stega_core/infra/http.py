from __future__ import annotations

import asyncio
import contextlib
import functools
from typing import TYPE_CHECKING, Any, Self

import httpx

if TYPE_CHECKING:
    import types
    from collections.abc import AsyncIterator, Iterator


class AsyncRateLimiter:

    def __init__(self, limit: int = 1, period: int = 1) -> None:
        self.limit = limit
        self.period = period
        self.lock = asyncio.Lock()
        self.signal = asyncio.Event()
        self._tasks = [asyncio.create_task(self.tick())]
        self.signal.set()

    async def tick(self) -> None:
        while True:
            await asyncio.sleep(self.period / self.limit)
            self.signal.set()

    async def __aenter__(self) -> Self:
        async with self.lock:
            await self.signal.wait()
            self.signal.clear()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: types.TracebackType | None,
    ) -> None:
        pass


def fetch(
    session: httpx.Client,
    url: str,
) -> httpx.Response:
    return session.get(url)


@contextlib.contextmanager
def acquire_session(
    base_url: str,
    params: dict[str, Any] | None = None,
    *,
    timeout: bool = True,
    timeout_params: dict[str, Any] | None = None,
) -> Iterator[httpx.Client]:
    # prepare timeout
    if not timeout:
        # disable timeout
        client_context_mgr = functools.partial(
            httpx.Client,
            base_url=base_url,
            params=params,
            http2=True,
            timeout=None,
        )
    elif timeout_params is not None:
        # timeout with custom settings
        timeout = httpx.Timeout(**timeout_params)
        client_context_mgr = functools.partial(
            httpx.Client,
            base_url=base_url,
            params=params,
            http2=True,
            timeout=timeout,
        )
    else:
        # default timeout
        client_context_mgr = functools.partial(
            httpx.Client,
            base_url=base_url,
            params=params,
            http2=True,
        )

    with client_context_mgr() as client:
        yield client


async def fetch_async(
    rate: AsyncRateLimiter,
    session: httpx.AsyncClient,
    url: str,
) -> httpx.Response:
    async with rate:
        return await session.get(url)


@contextlib.asynccontextmanager
async def acquire_async_session(
    base_url: str,
    params: dict[str, Any] | None = None,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        base_url=base_url,
        params=params,
        http2=True,
    ) as client:
        yield client
