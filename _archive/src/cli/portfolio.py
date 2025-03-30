from datetime import date

import click
import pandas as pd
import requests
import typing_extensions as T

from src.cli.entrypoint import cli
from src.models import get_annual_returns, get_cov_matrix, json_to_df


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
    price_df = get_annual_returns(df, starting_year)
    risk_df = get_cov_matrix(df, starting_year)

    title = "Portfolio Returns"
    click.echo(f"TIME RANGE => {starting_year} - {date.today().year}")
    click.echo(title)
    click.echo(banner(title))

    for symb_X in symbols:
        # Display header of each symbol
        avg_return = _get_avg_return(price_df, symb_X)
        risk = _get_risk(risk_df, symb_X)
        click.echo(f"{symb_X} => (return: {avg_return:.2%}) (risk: {risk:.2%}) ")

        # Display correlation with other symbols
        for symb_Y in symbols:
            if symb_X == symb_Y:
                continue
            corr = _get_corr(risk_df, symb_X, symb_Y)
            click.echo(f"  {symb_X} vs {symb_Y} => (corr: {corr:.2})")


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


def _get_avg_return(df: pd.DataFrame, symbol: str) -> float:
    return df.loc[df.index.get_level_values("symbol") == symbol]["annual_ret"].mean()


def _get_risk(df: pd.DataFrame, symbol: str) -> float:
    return df.at[symbol, symbol] ** 0.5


def _get_corr(df: pd.DataFrame, symbol_X: str, symbol_Y: str) -> float:
    cov = df.at[symbol_X, symbol_Y]
    std_X = _get_risk(df, symbol_X)
    std_Y = _get_risk(df, symbol_Y)
    return cov / (std_X * std_Y)
