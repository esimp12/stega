import click

from stega_cli.cli.commands import CLI_COMMANDS, GROUPS
from stega_cli.cli.generate import build_cli
from stega_cli.cli.groups import STATIC_GROUPS


@click.group()
def stega() -> None:
    """CLI for stega application."""


def run() -> None:
    for group in STATIC_GROUPS:
        stega.add_command(group)
    build_cli(stega, CLI_COMMANDS, GROUPS)
    stega()
