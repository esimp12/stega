import click
import requests

from src.cli.entrypoint import cli


@cli.group()
def prices():
    pass


@prices.command()
@click.argument("symbol")
def list(symbol: str):
    resp = requests.get(f"http://localhost:8000/prices/{symbol}")
    data = resp.json()
    click.echo(symbol)
    click.echo(banner(symbol))
    for res in data["prices"]:
        click.echo(f"{res['date']} | ${res['close']:,.2f}")


def banner(title: str, char: str = "-") -> str:
    return char * len(title)
