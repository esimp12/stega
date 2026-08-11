import asyncio
import json

import click
import httpx
from stega_core import decode

from stega_cli.config import create_config
from stega_cli.daemon.server import serve


@stega.group()
def events() -> None:
    """Inspect the edge event stream."""


@events.command()
@click.argument("topic")
def watch(topic: str) -> None:
    """Watch streamed events for a given topic."""
    asyncio.run(_watch(topic))


async def _watch(topic: str) -> None:
    config = create_config()
    url = f"{config.EDGE_SERVICE_URL}/api/events/{topic}"
    async with httpx.AsyncClient(timeout=None) as client, client.stream("GET", url) as response:
        response.raise_for_status()
        async for event in decode(response.aiter_lines()):
            click.echo(json.dumps(json.loads(event.data), indent=2))
