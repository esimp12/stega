from __future__ import annotations

from typing import TYPE_CHECKING

import uuid_utils as uuid
from stega_core import Query, ServiceResult

if TYPE_CHECKING:
    import asyncio
    from collections.abc import Callable

    from stega_core import Message, StegaServicePort


class RequestDispatcher:

    def __init__(
        self,
        port_factory: Callable[[], StegaServicePort],
        queue: asyncio.Queue,
    ) -> None:
        self._port_factory = port_factory
        self._queue = queue

    async def handle(self, message: Message) -> ServiceResult:
        if isinstance(message, Query):
            async with self._port_factory() as port:
                return await port.forward(message)

        correlation_id = str(uuid.uuid7())
        await self._queue.put((correlation_id, message))
        return ServiceResult(
            ok=True,
            msg="Request accepted.",
            result={"correlation_id": correlation_id},
        )
