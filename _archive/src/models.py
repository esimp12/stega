from datetime import date

import pandas as pd
import typing_extensions as T


def json_to_df(data: T.Mapping[str, T.Any]) -> pd.DataFrame:
    df = pd.DataFrame(
        data={
            "symbol": data["symbol"],
            "date": [elem["date"] for elem in data["prices"]],
            "price": [elem["close"] for elem in data["prices"]],
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df["symbol"] = df["symbol"].astype(str)
    df = df.set_index("date")
    return df


def get_daily_returns(
    df: pd.DataFrame,
    starting_year: int = 2015,
) -> pd.DataFrame:
    starting_date = f"{starting_year}-01-01"
    new_df = df.copy()
    new_df = new_df[new_df.index.get_level_values("date") >= starting_date]
    new_df["daily_ret"] = new_df.groupby(level="symbol")["price"].pct_change()
    new_df = new_df.dropna()
    return new_df


def get_cov_matrix(
    df: pd.DataFrame,
    starting_year: int = 2015,
    trading_days: int = 252,
) -> pd.DataFrame:
    df = get_daily_returns(df, starting_year)
    df = df.pivot_table(index="date", columns="symbol", values="daily_ret")
    return df.cov() * trading_days


def get_annual_returns(
    df: pd.DataFrame,
    starting_year: int = 2015,
) -> pd.DataFrame:
    """

    index                       columns
    -----                       -----
    date            symbol      annual_ret
    2023-12-31      AAPL        0.2
                    MSFT        0.1
                    TSLA        0.3
    2024-12-31      AAPL        0.1
                    MSFT        0.2
                    TSLA        0.4
    ...
    """
    df = get_daily_returns(df, starting_year)
    symbols = df.index.get_level_values("symbol").unique()
    current_year = date.today().year
    years = range(starting_year, current_year + 1)

    returns = []
    for symbol in symbols:
        for year in years:
            returns.append(
                {
                    "symbol": symbol,
                    "date": f"{year}-12-31",
                    "annual_ret": get_annual_return(df, symbol, year),
                }
            )

    return pd.DataFrame(returns).set_index(["date", "symbol"])


def get_annual_return(
    df: pd.DataFrame,
    symbol: str,
    year: int,
    trading_days: int = 252,
) -> float:
    """
    Get the annual return of a symbol for a specific year.
    """
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    year_df = df.loc[
        (df.index.get_level_values("symbol") == symbol)
        & (df.index.get_level_values("date") >= start_date)
        & (df.index.get_level_values("date") <= end_date)
    ]
    num_returns = year_df.shape[0]
    return (year_df["daily_ret"] + 1).cumprod().pow(trading_days / num_returns).iloc[
        -1
    ] - 1
