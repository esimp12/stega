from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from stega_core import View

if TYPE_CHECKING:
    from stega_portfolio.domain.portfolio import Portfolio, PortfolioAsset


@dataclass(frozen=True, kw_only=True)
class AssetView(View):
    symbol: str
    weight: float

    @classmethod
    def from_asset(cls, asset: PortfolioAsset) -> AssetView:
        return cls(
            symbol=asset.symbol,
            weight=asset.weight,
        )


@dataclass(frozen=True, kw_only=True)
class PortfolioView(View):
    portfolio_id: str
    name: str
    assets: list[AssetView]

    @classmethod
    def from_portfolio(cls, portfolio: Portfolio) -> PortfolioView:
        return cls(
            portfolio_id=portfolio.portfolio_id,
            name=portfolio.name,
            assets=[AssetView.from_asset(asset) for asset in portfolio.assets],
        )
