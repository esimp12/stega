from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import httpx
from stega_core import Event, decode

from stega_cli.daemon.handlers import CACHE_HANDLERS
from stega_cli.ports.cache import action as action_db
from stega_cli.ports.cache import db

if TYPE_CHECKING:
    from stega_cli.config import CliConfig


_BACKOFF_MIN: float = 1.0
_BACKOFF_MAX: float = 30.0


async def run_tail(config: CliConfig, topic: str) -> None:
    url = f"{config.EDGE_SERVICE_URL}/api/events/{topic}"
    backoff = _BACKOFF_MIN
    async with httpx.AsyncClient(timeout=None) as client:
        while True:
            try:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    backoff = _BACKOFF_MIN
                    async for event in decode(response.aiter_lines()):
                        await _apply(config, json.loads(event.data))
            except Exception:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, _BACKOFF_MAX)


async def _apply(config: CliConfig, data: dict) -> None:
    event = Event.deserialize(data)
    with db.acquire_connection(config.db_path) as conn:
        action_db.record(conn, event.correlation_id, event.topic)
        handler = CACHE_HANDLERS.get(type(event))
        if handler is not None:
            handler(conn, event)
        conn.commit()
