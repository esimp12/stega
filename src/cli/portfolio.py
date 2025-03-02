import click
import requests
import typing_extensions as T

from src.cli.entrypoint import cli


@cli.group()
def portfolio():
    pass


@portfolio.command()
@click.argument("weights")
def create(weights: str):
    weights = parse_weights(weights)

    prices = {}
    for symbol, _ in weights.items():
        resp = requests.get(f"http://localhost:8000/prices/{symbol}")
        data = resp.json()
        prices[symbol] = [(res["date"], res["close"]) for res in data["prices"]]

    click.echo("Portfolio")
    click.echo(banner("Portfolio"))
    click.echo(" ".join(prices.keys()))


def parse_weights(filename: str) -> T.Mapping[str, float]:
    weights = {}
    with open(filename, encoding="utf-8") as fd:
        for line in fd.readlines():
            symbol, weight = line.split()
            weights[symbol] = float(weight)
    return weights


def banner(title: str, char: str = "-") -> str:
    return char * len(title)
