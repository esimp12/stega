from __future__ import annotations

import asyncio
from collections import deque
from contextlib import AsyncExitStack
from time import monotonic
from typing import Protocol, Self


class RateLimiter(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *exc: object) -> None: ...


class SmoothingRateLimiter:
    def __init__(self, limit: int, period: float = 1.0) -> None:
        self._interval = period / limit
        self._lock = asyncio.Lock()
        self._next = 0.0

    async def __aenter__(self) -> Self:
        async with self._lock:
            target = max(monotonic(), self._next)
            self._next = target + self._interval
        delay = target - monotonic()
        if delay > 0:
            await asyncio.sleep(delay)
        return self

    async def __aexit__(self, *_: object) -> None: ...


class QuotaRateLimiter:
    def __init__(self, limit: int, period: float) -> None:
        self._limit = limit
        self._period = period
        self._lock = asyncio.Lock()
        self._hits = deque[float] = deque()

    async def __aenter__(self) -> Self:
        while True:
            async with self._lock:
                now = monotonic()
                cutoff = now - self._period
                while self._hits and self._hits[0] <= cutoff:
                    self._hits.popleft()
                if len(self._hits) < self._limit:
                    self._hits.append(now)
                    return self
                wait = self._hits[0] + self._period - now
            await asyncio.sleep(wait)

    async def __aexit__(self, *_: object) -> None: ...


class RateLimiterStack:
    def __init__(self, limiters: list[RateLimiter]) -> None:
        self._limiters = limiters
        self._entered: AsyncExitStack | None = None

    async def __aenter__(self) -> Self:
        async with AsyncExitStack() as stack:
            for limiter in self._limiters:
                await stack.enter_async_context(limiter)
            self._stack = stack.pop_all()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._stack.__aexit__(*exc)
