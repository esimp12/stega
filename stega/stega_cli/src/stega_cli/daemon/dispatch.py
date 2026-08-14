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
        db_path: str,
    ) -> None:
        self._port_factory = port_factory
        self._queue = queue
        self._db_path = db_path

    async def handle(self, message: Message) -> ServiceResult:
        if isinstance(message, Query):
            cached = self._read_cache(message)
            if cached is not None:
                return cached
            async with self._port_factory() as port:
                result = await port.forward(message)
            if result.result is not None:
                self._write_back(message, result.result)
            return result

        correlation_id = str(uuid.uuid7())
        await self._queue.put((correlation_id, message))
        return ServiceResult(
            ok=True,
            msg="Request accepted.",
            result={"correlation_id": correlation_id},
        )

    def _read_cache(self, query: Query) -> ServiceResult | None:
        reader = CACHE_READERS.get(type(query))
        if reader is None:
            return None
        with db.acquire_connection(self._db_path) as conn:
            view = reader(conn, query)
        return None if view is None else ServiceResult(ok=True, msg="OK", result=view)

    def _write_back(self, query: Query, data: dict) -> None:
        writer = CACHE_WRITEBACKS.get(type(query))
        if writer is None:
            return
        with db.acquire_connection(self._db_path) as conn:
            writer(conn, data)
            conn.commit()
