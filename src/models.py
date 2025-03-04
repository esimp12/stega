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
