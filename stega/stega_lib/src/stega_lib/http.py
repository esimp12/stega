"""HTTP client utilities for synchronous and asynchronous requests."""

import asyncio
import contextlib
import types
import typing as T

import httpx


class AsyncRateLimiter:
    """Asynchronous rate limiter that allows a limited number of requests per period."""

    def __init__(self, limit: int = 1, period: int = 1) -> None:
        """Initialize the rate limiter.

        Attributes:
            limit (int): Maximum number of requests allowed in the period.
            period (int): Time period in seconds during which the requests are limited.
        """
        self.limit = limit
        self.period = period
        self.lock = asyncio.Lock()
        self.signal = asyncio.Event()
        self._tasks = [asyncio.create_task(self.tick())]
        self.signal.set()

    async def tick(self) -> None:
        """Periodically set the signal to allow requests."""
        while True:
            await asyncio.sleep(self.period / self.limit)
            self.signal.set()

    async def __aenter__(self) -> T.Self:
        """Acquire the rate limiter lock and wait for the signal to proceed."""
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
        """Exit the rate limiter context manager."""


def fetch(
    session: httpx.Client,
    url: str,
) -> httpx.Response:
    """Fetch a URL using the provided synchronous HTTP client session.

    Args:
        session (httpx.Client): The HTTP client session to use for the request.
        url (str): The URL to fetch.

    Returns:
        httpx.Response: The response object containing the result of the request.

    """
    return session.get(url)


@contextlib.contextmanager
def acquire_session(
    base_url: str,
    params: dict[str, T.Any] | None = None,
) -> T.Generator[httpx.Client, None, None]:
    """Acquire a synchronous HTTP client session for use as a context manager.

    Args:
        base_url (str): The base URL for the HTTP client.
        params (dict[str, T.Any] | None): Optional parameters to include in the requests.

    Yields:
        httpx.Client: A context manager that yields an HTTP client session.
    """
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
) -> httpx.Response:
    """Fetch a URL using the provided asynchronous HTTP client session.

    Args:
        rate (AsyncRateLimiter): The rate limiter to control the request rate.
        session (httpx.AsyncClient): The asynchronous HTTP client session to use for the request.
        url (str): The URL to fetch.

    Returns:
        httpx.Response: The response object containing the result of the request.
    """
    async with rate:
        return await session.get(url)


@contextlib.asynccontextmanager
async def acquire_async_session(
    base_url: str,
    params: dict[str, T.Any] | None = None,
) -> T.AsyncGenerator[httpx.AsyncClient, None]:
    """Acquire an asynchronous HTTP client session for use as a context manager.

    Args:
        base_url (str): The base URL for the HTTP client.
        params (dict[str, T.Any] | None): Optional parameters to include in the requests.

    Yields:
        httpx.AsyncClient: A context manager that yields an asynchronous HTTP client session.
    """
    async with httpx.AsyncClient(
        base_url=base_url,
        params=params,
        http2=True,
    ) as client:
        yield client
