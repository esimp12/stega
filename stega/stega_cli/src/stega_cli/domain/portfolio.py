from dataclasses import dataclass


@dataclass
class PortfolioAsset:
    """Data representation of a portfolio asset.

    Attributes:
        symbol: A str of the stock symbol for the asset.
        weight: A float of the weight contribution of the asset towards
            the portfolio.

    """

    symbol: str
    weight: float


@dataclass
class Portfolio:
    """Data representation of a portfolio.

    Attributes:
        portfolio_id: A str of the unique ID of the portfolio.
        name: A str of the portfolio name.
        assets: A list of portfolio assets as PortfolioAsset instances. An asset contains
            both a symbol and a weight.

    """

    portfolio_id: str
    name: str
    assets: list[PortfolioAsset]
