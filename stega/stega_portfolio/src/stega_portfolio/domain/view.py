from dataclasses import dataclass

from stega_core import View


@dataclass(frozen=True, kw_only=True)
class AssetView(View):
    symbol: str
    weight: float


@dataclass(frozen=True, kw_only=True)
class PortfolioView(View):
    portfolio_id: str
    name: str
    assets: list[AssetView]


@dataclass(frozen=True, kw_only=True)
class PortfolioListView(View):
    portfolios: list[PortfolioView]
