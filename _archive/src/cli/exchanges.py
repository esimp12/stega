import click

from src.cli.entrypoint import cli
from src.external.symbols import get_sp500_symbols


@cli.group()
def exchanges():
    pass


@exchanges.command()
def list_sp500():
    symbols = get_sp500_symbols()
    for symbol in symbols:
        click.echo(symbol)
