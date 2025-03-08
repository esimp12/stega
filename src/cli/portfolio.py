from datetime import date

import click
import pandas as pd
import requests
import typing_extensions as T

from src.cli.entrypoint import cli
from src.models import get_annual_returns, json_to_df


@cli.group()
def portfolio():
    pass


@portfolio.command()
@click.argument("filename")
@click.option("--starting-year", type=int, default=2015)
def create(
    filename: str,
    starting_year: int,
):
    weights = parse_weights(filename)
    symbols = list(weights.keys())
    df = get_prices_df(symbols)
    df = get_annual_returns(df, starting_year)

    title = "Portfolio Returns"
    click.echo(f"TIME RANGE => {starting_year} - {date.today().year}")
    click.echo(title)
    click.echo(banner(title))

    for symbol in symbols:
        avg_return = df.loc[df.index.get_level_values("symbol") == symbol][
            "annual_ret"
        ].mean()
        click.echo(f"{symbol}: {avg_return:.2%}")


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
