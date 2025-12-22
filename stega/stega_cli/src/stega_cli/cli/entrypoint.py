"""CLI entrypoint for stega portfolio management application."""

import importlib
from pathlib import Path

import click


_IGNORE_MODULES = (
    Path(__file__).name,
    "__init__.py",
    "utils.py",
    "command.py",
)


@click.group()
def stega() -> None:
    """CLI for stega portfolio management application."""


def register_commands() -> None:
    file_import = __spec__.name
    root_import = ".".join(file_import.split(".")[:-1])
    root = Path(__file__).parent.resolve()
    for path in root.iterdir():
        if path.name in _IGNORE_MODULES:
            continue
        if path.is_file():
            importlib.import_module(f"{root_import}.{path.stem}")


def run() -> None:
    """Run the stega CLI."""
    register_commands()
    stega()
