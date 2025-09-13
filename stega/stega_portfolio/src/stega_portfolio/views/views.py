"""Application views for handling read only service requests."""

import typing as T
from dataclasses import dataclass

from stega_portfolio.domain.portfolio import PortfolioAsset, Portfolio 


class View:
    """Represents a generic view."""


@dataclass
class AssetView(View):
    """Represents an Assets view."""
    symbol: str
    weight: float

    @classmethod
    def from_asset(cls, asset: PortfolioAsset) -> T.Self:
        """Create an AssetView from a PortfolioAsset."""
        return cls(
            symbol=asset.symbol,
            weight=asset.weight,
        )


@dataclass
class PortfolioView(View):
    """Represents a Portfolios view."""
    name: str
    assets: list[AssetView]


    @classmethod
    def from_portfolio(cls, portfolio: Portfolio) -> T.Self:
        """Create a PortfolioView from a Portfolio."""
        return cls(
            name=portfolio.name,
            assets=[
                AssetView.from_asset(asset)
                for asset in portfolio.assets
            ],
        )
