from __future__ import annotations

from typing import Callable

from stega_core.domain import AppError
from stega_core.service.channel import Channel
from stega_core.service.transport import AbstractTransport, ServiceResult


class StegaServicePort:

    def __init__(
        self,
        channel_factory: Callable[[], Channel],
        transport_type: type[AbstractTransport],
    ) -> None:
        self._channel_factory = channel_factory
        self._transport_type = transport_type
        self._channel: Channel | None = None
        self._transport: AbstractTransport | None = None

    async def __aenter__(self) -> StegaServicePort:
        self._channel = self._channel_factory()
        self._transport = self._transport_type(self._channel)
        await self._channel.open()
        return self

    async def __aexit__(self, *exc: object) -> None:
        try:
            if self._channel is not None:
                await self._channel.close()
        finally:
            self._channel = None
            self._transport = None

    async def _dispatch(self, message: Message) -> ServiceResult:
        if self._transport is None:
            err_msg = f"{type(self).__name__} must be used within `async with`"
            raise RuntimeError(err_msg)
        result = await self._transport.dispatch(message)
        if not result.ok:
            raise AppError(result.msg)
        return result

    async def forward(self, message: Message) -> ServiceResult:
        return await self._dispatch(message)
