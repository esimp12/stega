from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import click

from stega_cli.config import create_config
from stega_cli.daemon.server import serve

_SYSTEMCTL: str = "/usr/bin/systemctl"
_UNIT_TEMPLATE: str = """\
[Unit]
Description=stega CLI background daemon
After=network.target
StartLimitBurst=5
StartLimitIntervalSec=30

[Service]
Type=simple
ExecStart=%h/.local/bin/stega daemon run
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
def daemon() -> None:
    """Manager the local stega daemon."""


@daemon.command()
def run() -> None:
    """Run the daemon in the foreground."""
    asyncio.run(serve(create_config()))


@daemon.command()
@click.option("--force", is_flag=True, help="Overwrite an existing unit file.")
def install(*, force: bool) -> None:
    """Install and start the daemon as a systemd user service."""
    config = create_config()
    unit_dir = Path.home() / ".config" / "systemd" / "user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    unit_path = unit_dir / config.SERVICE_UNIT
    if force or not unit_path.exists():
        unit_path.write_text(_UNIT_TEMPLATE)
    _systemctl("daemon-reload")
    _systemctl("enable", config.SERVICE_UNIT)
    _systemctl("restart", config.SERVICE_UNIT)


@daemon.command()
def uninstall() -> None:
    """Stop and disable the daemon systemd user service."""
    unit = create_config().SERVICE_UNIT
    _systemctl("stop", unit)
    _systemctl("disable", unit)


@daemon.command()
def status() -> None:
    """Show the daemon systemd status."""
    unit = create_config().SERVICE_UNIT
    proc = subprocess.run(
        [_SYSTEMCTL, "--user", "status", unit],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    click.echo(proc.stdout.decode())


def _systemctl(*args: str) -> None:
    subprocess.run([_SYSTEMCTL, "--user", *args], check=True)
