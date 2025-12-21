"""CLI entrypoint for stega portfolio management application."""

from pathlib import Path

import subprocess
import click

from stega_lib import http
from stega_cli.config import create_config
from stega_cli.daemon import acquire_connection, send_command, read_command, serve 

_SYSTEMD_UNIT_FILE = """
[Unit]
Description=stega CLI background daemon
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/stega start-daemon
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=2
WorkingDirectory=%h
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""


@click.group()
def stega() -> None:
    """CLI for stega portfolio management application."""


@click.option(
    "--force",
    is_flag=True,
    help="Force overwriting the systemd user service unit file."
)
@stega.command()
def install_daemon(force: bool) -> None:
    config = create_config()

    # Create systemd unit file
    systemd_user_path = Path.home() / ".config" / "systemd" / "user"
    systemd_user_path.mkdir(parents=True, exist_ok=True)
    systemd_unit_file_path = systemd_user_path / config.STEGA_CLI_SYSTEMD_UNIT_NAME
    if not systemd_unit_file_path.exists() or force:
        systemd_unit_file_path.write_text(_SYSTEMD_UNIT_FILE)

    subprocess.run(["systemctl", "--user", "daemon-reload"])
    subprocess.run(["systemctl", "--user", "enable", config.STEGA_CLI_SYSTEMD_UNIT_NAME])
    subprocess.run(["systemctl", "--user", "restart", config.STEGA_CLI_SYSTEMD_UNIT_NAME])


@stega.command()
def start_daemon() -> None:
    config = create_config()
    serve(config.sock_path)


@stega.command()
def status() -> None:
    pass


@stega.command()
def stop_daemon() -> None:
    pass


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

    config = create_config()
    with acquire_connection(config.sock_path) as conn:
        send_command(conn, cmd)
        # resp = read_command(conn)


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
    # TODO: Generate a correlation id. Send this command to the daemon. Have the dameon spawn a new
    # thread which runs this code. Print out the correlation/status id.
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
