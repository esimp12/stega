# ruff: noqa:S603

import asyncio
import subprocess
from pathlib import Path

import click

from stega_cli.cli.entrypoint import stega
from stega_cli.config import create_config
from stega_cli.daemon import serve

_SYSTEMCTL_BIN_PATH: str = "/usr/bin/systemctl"
_SYSTEMD_UNIT_FILE: str = """
[Unit]
Description=stega CLI background daemon
After=network.target
StartLimitBurst=5
StartLimitIntervalSec=30

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
    help="Force overwriting the systemd user service unit file.",
)
@daemon.command()
def install(*, force: bool) -> None:
    """Install the daemon as a systemd user service."""
    config = create_config()

    # Create systemd unit file
    systemd_user_path = Path.home() / ".config" / "systemd" / "user"
    systemd_user_path.mkdir(parents=True, exist_ok=True)
    systemd_unit_file_path = systemd_user_path / config.STEGA_CLI_SYSTEMD_UNIT_NAME
    if not systemd_unit_file_path.exists() or force:
        systemd_unit_file_path.write_text(_SYSTEMD_UNIT_FILE)

    unit = _get_systemd_unit()
    subprocess.run([_SYSTEMCTL_BIN_PATH, "--user", "daemon-reload"], check=True)
    subprocess.run([_SYSTEMCTL_BIN_PATH, "--user", "enable", unit], check=True)
    subprocess.run([_SYSTEMCTL_BIN_PATH, "--user", "restart", unit], check=True)


@daemon.command()
def start() -> None:
    """Serve the daemon to listen for CLI commands."""
    config = create_config()
    coro = serve(config.sock_path, config.db_path)
    asyncio.run(coro)


@daemon.command()
def status() -> None:
    """Get info about the daemon systemd status."""
    unit = _get_systemd_unit()
    proc = subprocess.run(
        [
            _SYSTEMCTL_BIN_PATH,
            "--user",
            "status",
            unit,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    click.echo(proc.stdout)


@daemon.command()
def uninstall() -> None:
    """Stop and disable the daemon systemd user service."""
    unit = _get_systemd_unit()
    subprocess.run([_SYSTEMCTL_BIN_PATH, "--user", "stop", unit], check=True)
    subprocess.run([_SYSTEMCTL_BIN_PATH, "--user", "disable", unit], check=True)


def _get_systemd_unit() -> str:
    config = create_config()
    return config.STEGA_CLI_SYSTEMD_UNIT_NAME
