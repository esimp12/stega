"""CLI entrypoint for stega portfolio management application."""

import click

from stega_lib import http
from stega_cli.config import create_config
from stega_cli.daemon import acquire_connection, send_command, read_command, serve 


@click.group()
def stega() -> None:
    """CLI for stega portfolio management application."""


@stega.command()
def serve_daemon() -> None:
    sock_path = "/tmp/stega.sock"
    serve(sock_path)


@click.argument("portfolio_id")
@stega.command()
def get_portfolio(portfolio_id: str) -> None:
    """Command to get a portfolio."""
    cmd = {
        "type": "GetPortfolio",
        "args": {
            "portfolio_id": portfolio_id,
        },
    }

    sock_path = "/tmp/stega.sock"
    with acquire_connection(sock_path) as conn:
        send_command(conn, cmd)
        resp = read_command(conn)


@stega.command()
def list_portfolios() -> None:
    """Command to list existing portfolios."""
    config = create_config()
    with http.acquire_session(config.core_service_url) as session:
        resp = session.get("portfolios")
        resp.raise_for_status()
        data = resp.json()["result"]
    
    _echo_banner("PORTFOLIOS")
    click.echo()
    for idx, portfolio in enumerate(data):
        name = portfolio["name"]
        assets = portfolio["assets"]
        _echo_banner(f"Portfolio #{idx+1}", char="-")
        click.echo(f"Name: {name}")
        click.echo("Assets:")
        for asset in assets:
            symbol = asset["symbol"]
            weight = asset["weight"]
            click.echo(f"  - {symbol} ({weight:.2f})")
        click.echo()


@click.argument("name")
@click.option(
    "-f",
    "--portfolio-file",
    help="A csv of assets and weights to create a portfolio from.",
)
@stega.command()
def create_portfolio(
    name: str,
    portfolio_file: str,
) -> None:
    """Command to create a new portfolio."""
    click.echo(f"Creating portfolio '{name}' from {portfolio_file}...")
    config = create_config()
    payload = _get_portfolio_payload(name, portfolio_file)
    with http.acquire_session(config.core_service_url) as session:
        resp = session.post("portfolios", json=payload)
        resp.raise_for_status()
        data = resp.json()
        click.echo(data)


def _get_portfolio_payload(name: str, portfolio_file: str) -> dict[str, str | dict[str, float]]:
    payload = {"name": name, "assets": {} }
    with open(portfolio_file, "r", encoding="utf-8") as fd:
        for line in fd.readlines():
            symbol, weight = line.split(",")
            symbol = symbol.strip()
            weight = float(weight.strip())
            payload["assets"][symbol] = weight
    return payload


# TODO: Move the following to utils
def _echo_banner(title: str, char: str = "=") -> None:
    banner = char * len(title)
    click.echo(title)
    click.echo(banner)


def run() -> None:
    """Run the stega CLI."""
    stega()
