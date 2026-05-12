from dataclasses import dataclass


@dataclass
class PortfolioAsset:
    """Class to represent an asset in a portfolio.

    Attributes:
        symbol: A str of the stock symbol of the asset.
        weight: A float of the weight contribution of the asset towards
            the portfolio.

    """

    symbol: str
    weight: float


@dataclass
class PortfolioData:
    """Portfolio class to represent a portfolio of stocks.

    Attributes:
        portfolio_id: A str of the unique ID of the portfolio.
        name: A str of the portfolio name.
        assets: A list of portfolio assets as PortfolioAsset instances.

    """

    portfolio_id: str
    name: str
    assets: list[PortfolioAsset]
