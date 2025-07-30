"""Domain model for a portfolio of stocks."""

from dataclasses import dataclass


@dataclass
class PortfolioAsset:
    """Class to represent an asset in a portfolio.

    Attributes:
        symbol (str): The stock symbol of the asset.
        weight (float): The weight of the asset in the portfolio.

    """

    symbol: str
    weight: float


@dataclass
class PortfolioData:
    """Portfolio class to represent a portfolio of stocks.

    Attributes:
        name (str): The name of the portfolio.
        assets (list[PortfolioAsset]): A list of assets in the portfolio.

    """

    name: str
    assets: list[PortfolioAsset]
