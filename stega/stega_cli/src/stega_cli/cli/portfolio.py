import click

from stega_cli.config import create_config
from stega_cli.cli.entrypoint import stega
from stega_cli.cli.utils import echo_banner
from stega_cli.daemon import acquire_connection, send_command, read_command
from stega_cli.domain.request import (
    GetPortfolioRequest,
    ListPortfoliosRequest,
    CreatePortfolioRequest,
    CommandRequest,
    Response,
)
from stega_lib import http


@stega.group()
def portfolio() -> None:
    """Commands for managing portfolios."""


@click.argument("portfolio_id")
@portfolio.command()
def get(portfolio_id: str) -> None:
    """Command to get a portfolio."""
    cmd = GetPortfolioRequest(portfolio_id)
    resp = _send_daemon_command(cmd)
    status = resp["status"]
    result = resp["result"]
    if status == "error":
        click.echo(click.style(result, fg="red"))
    else:
        _disp_portfolio(result)


@portfolio.command()
def list() -> None:
    """Command to list existing portfolios."""
    cmd = ListPortfoliosRequest()
    resp = _send_daemon_command(cmd)
    data = resp["result"]
    echo_banner("PORTFOLIOS")
    for portfolio in data:
        _disp_portfolio(portfolio)


@click.argument("name")
@click.option(
    "-f",
    "--portfolio-file",
    help="A csv of assets and weights to create a portfolio from.",
)
@portfolio.command()
def create(
    name: str,
    portfolio_file: str,
) -> None:
    """Command to create a new portfolio."""
    click.echo(f"Creating portfolio '{name}' from {portfolio_file}...")
    payload = _get_portfolio_payload(name, portfolio_file)
    cmd = CreatePortfolioRequest(
        name=payload["name"],
        assets=payload["assets"],
    )
    resp = _send_daemon_command(cmd)
    result = resp["result"]
    correlation_id = result["correlation_id"]
    click.echo(f"Successfully submitted request to create portfolio. Query latest result with id - {correlation_id}")


def _disp_portfolio(portfolio: dict[str, str | list[dict[str, str | float]]]) -> None:
    portfolio_id = portfolio["portfolio_id"]
    name = portfolio["name"]
    assets = portfolio["assets"]
    click.echo()
    click.echo(f"ID: {portfolio_id}")
    click.echo(f"Name: {name}")
    click.echo("Assets:")
    for asset in assets:
        symbol = asset["symbol"]
        weight = asset["weight"]
        click.echo(f"  - {symbol} ({weight:.2f})")


def _send_daemon_command(cmd: CommandRequest) -> Response:
    config = create_config()
    with acquire_connection(config.sock_path) as conn:
        send_command(conn, cmd.to_dict())
        return read_command(conn)


def _get_portfolio_payload(name: str, portfolio_file: str) -> dict[str, str | dict[str, float]]:
    payload = {"name": name, "assets": {} }
    with open(portfolio_file, "r", encoding="utf-8") as fd:
        for line in fd.readlines():
            symbol, weight = line.split(",")
            symbol = symbol.strip()
            weight = float(weight.strip())
            payload["assets"][symbol] = weight
    return payload

