import click
import requests

from src.cli.entrypoint import cli


@cli.group()
def symbols():
    pass


@symbols.command()
def list():
    results = requests.get("http://localhost:8000/symbols")
    for res in results.json():
        click.echo(f"{res['id']} - {res['symbol']}")
