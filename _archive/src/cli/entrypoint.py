import importlib
from pathlib import Path

import click


@click.group()
def cli():
    pass


def register_commands():
    file_import = __spec__.name
    root_import = ".".join(file_import.split(".")[:-1])
    root = Path(__file__).parent.resolve()
    for path in root.iterdir():
        if path.name == "__init__.py":
            continue
        if path.is_file():
            importlib.import_module(f"{root_import}.{path.stem}")


def run():
    register_commands()
    cli()
