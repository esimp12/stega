from __future__ import annotations

import contextlib
import functools
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator


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
