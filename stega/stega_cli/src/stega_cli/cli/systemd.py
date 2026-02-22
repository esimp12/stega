import asyncio
import subprocess
from pathlib import Path

import click

from stega_cli.config import create_config
from stega_cli.cli.entrypoint import stega
from stega_cli.daemon import serve

# TODO: Change this to a template so that the stega install path and command name can be modified
_SYSTEMD_UNIT_FILE = """
[Unit]
Description=stega CLI background daemon
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/stega daemon start
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=2
WorkingDirectory=%h
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""


@stega.group()
def daemon() -> None:
    """Commands for managing local stega CLI daemon."""


@click.option(
    "--force",
    is_flag=True,
    help="Force overwriting the systemd user service unit file."
)
@daemon.command()
def install(force: bool) -> None:
    """Install the daemon as a systemd user service."""
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


@daemon.command()
def start() -> None:
    """Serve the daemon to listen for CLI commands."""
    config = create_config()
    asyncio.run(serve(config.sock_path))


@daemon.command()
def status() -> None:
    """Get info about the daemon systemd status."""
    config = create_config()
    proc = subprocess.run(
        [
            "systemctl",
            "--user",
            "status",
            config.STEGA_CLI_SYSTEMD_UNIT_NAME,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    click.echo(proc.stdout)


@daemon.command()
def stop() -> None:
    """Stop and disable the daemon systemd user service."""
    config = create_config()
    subprocess.run(["systemctl", "--user", "stop", config.STEGA_CLI_SYSTEMD_UNIT_NAME])
    subprocess.run(["systemctl", "--user", "disable", config.STEGA_CLI_SYSTEMD_UNIT_NAME])

