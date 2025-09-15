"""CLI entrypoint for stega portfolio management application."""

import click

from stega_lib import http
from stega_cli.config import create_config


@click.group()
def stega() -> None:
    """CLI for stega portfolio management application."""


@stega.command()
def list_portfolios() -> None:
    """Command to list existing portfolios."""
    click.echo("List portfolios...")
    config = create_config()
    with http.acquire_session(config.core_service_url) as session:
        resp = session.get("portfolios")
        resp.raise_for_status()
        data = resp.json()
        click.echo(data)


def run() -> None:
    """Run the stega CLI."""
    stega()
