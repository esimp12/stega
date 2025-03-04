import click
import pandas as pd
import requests
import typing_extensions as T

from src.cli.entrypoint import cli
from src.models import get_daily_returns, json_to_df


@cli.group()
def portfolio():
    pass


@portfolio.command()
@click.argument("filename")
def create(filename: str):
    weights = parse_weights(filename)
    symbols = list(weights.keys())
    prices_df = get_prices_df(symbols)
    prices_df = get_daily_returns(prices_df)
    click.echo("Portfolio")
    click.echo(banner("Portfolio"))
    click.echo(" ".join(symbols))


def parse_weights(filename: str) -> T.Mapping[str, float]:
    weights = {}
    with open(filename, encoding="utf-8") as fd:
        for line in fd.readlines():
            symbol, weight = line.split()
            weights[symbol] = float(weight)
    return weights


def get_prices_df(symbols: T.List[str]) -> pd.DataFrame:
    dfs = []
    for symbol in symbols:
        resp = requests.get(f"http://localhost:8000/prices/{symbol}")
        data = resp.json()
        dfs.append(json_to_df(data))
    return pd.concat(dfs).set_index("symbol", append=True).sort_index()


def banner(title: str, char: str = "-") -> str:
    return char * len(title)
