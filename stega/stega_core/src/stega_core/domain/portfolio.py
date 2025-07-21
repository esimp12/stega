from dataclasses import dataclass

import typing_extensions as T


@dataclass
class Portfolio:
    """Portfolio class to represent a portfolio of stocks.

    Attributes:
        name (str): The name of the portfolio.
        assets (Mapping[str, float]): A mapping of stock symbols to their
            respective weights in the portfolio.

    """

    name: str
    assets: T.Mapping[str, float]
