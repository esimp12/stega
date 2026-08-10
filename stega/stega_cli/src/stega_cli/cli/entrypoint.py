import asyncio
import json

import click
import httpx

from stega_cli.cli.generate import build_cli
from stega_cli.cli.commands import CLI_COMMANDS, GROUPS
from stega_cli.config import create_config
from stega_cli.daemon.server import serve


@click.group()
def stega() -> None:
    """CLI for stega application."""


@stega.group()
def daemon() -> None:
    """Manage the local stega daemon."""


@daemon.command(name="run")
def run_daemon() -> None:
    """Run the daemon in the foreground."""
    asyncio.run(serve(create_config()))


@stega.group()
def events() -> None:
    """Inspect the edge event stream."""


@click.argument("topic")
@events.command()
def watch(topic: str) -> None:
    """Watch streamed events for a given topic."""
    asyncio.run(_watch(topic))


async def _watch(topic: str) -> None:
    config = create_config()
    url = f"{config.EDGE_SERVICE_URL}/api/events/{topic}"
    async with httpx.AsyncClient(timeout=None) as client:
        async for sse in source.aiter_sse():
            click.echo(json.dumps(json.loads(sse.data), indent=2))


def run() -> None:
    build_cli(stega, CLI_COMMANDS, GROUPS)
    stega()
