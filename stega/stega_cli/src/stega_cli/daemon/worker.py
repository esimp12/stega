from __future__ import annotations

from typing import TYPE_CHECKING

from stega_core import set_context

if TYPE_CHECKING:
    import asyncio
    from collections.abc import Callable

    from stega_core import StegaServicePort


async def run_writer(
    queue: asyncio.Queue,
    port_factory: Callable[[], StegaServicePort],
) -> None:
    while True:
        correlation_id, message = await queue.get()
        try:
            set_context({"correlation_id": correlation_id})
            async with port_factory() as port:
                await port.forward(message)
        except Exception:
            pass
        finally:
            queue.task_done()
