import click

from stega_cli.config import create_config
from stega_cli.cli.entrypoint import stega
from stega_cli.cli.utils import echo_banner
from stega_cli.daemon import acquire_connection, send_command 
from stega_cli.domain.command import GetPortfolio, ListPortfolios, CreatePortfolio
from stega_lib import http


@stega.group()
def portfolio() -> None:
    """Commands for managing portfolios."""


@click.argument("portfolio_id")
@portfolio.command()
def get(portfolio_id: str) -> None:
    """Command to get a portfolio."""
    config = create_config()
    cmd = GetPortfolio(portfolio_id)
    with acquire_connection(config.sock_path) as conn:
        send_command(conn, cmd.to_dict())


@portfolio.command()
def list() -> None:
    """Command to list existing portfolios."""
    config = create_config()
    cmd = ListPortfolios()

    with http.acquire_session(config.core_service_url) as session:
        resp = session.get("portfolios")
        resp.raise_for_status()
        data = resp.json()["result"]
    
    echo_banner("PORTFOLIOS")
    click.echo()
    for idx, portfolio in enumerate(data):
        name = portfolio["name"]
        assets = portfolio["assets"]
        echo_banner(f"Portfolio #{idx+1}", char="-")
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
@portfolio.command()
def create(
    name: str,
    portfolio_file: str,
) -> None:
    """Command to create a new portfolio."""
    # TODO: Generate a correlation id. Send this command to the daemon. Have the dameon spawn a new
    # thread which runs this code. Print out the correlation/status id.
    click.echo(f"Creating portfolio '{name}' from {portfolio_file}...")
    config = create_config()
    payload = _get_portfolio_payload(name, portfolio_file)
    cmd = CreatePortfolio(
        name=payload["name"],
        assets=payload["assets"],
    )

    with acquire_connection(config.sock_path) as conn:
        send_command(conn, cmd.to_dict())


def _get_portfolio_payload(name: str, portfolio_file: str) -> dict[str, str | dict[str, float]]:
    payload = {"name": name, "assets": {} }
    with open(portfolio_file, "r", encoding="utf-8") as fd:
        for line in fd.readlines():
            symbol, weight = line.split(",")
            symbol = symbol.strip()
            weight = float(weight.strip())
            payload["assets"][symbol] = weight
    return payload

