import json

import click
from stega_lib import http

from stega_cli.cli.entrypoint import stega
from stega_cli.config import create_config


@stega.group()
def events() -> None:
    """Commands for interacting with stega events."""


@click.argument("topic")
@events.command()
def watch(topic: str) -> None:
    """Watch incoming streamed events for a given topic."""
    config = create_config()

    topic_url = f"events/{topic}"
    with http.acquire_session(config.core_service_url, timeout=False) as session:
        with session.stream("GET", topic_url) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                click.echo(data)
