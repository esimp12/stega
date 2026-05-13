from dataclasses import dataclass


@dataclass
class PortfolioAsset:
    symbol: str
    weight: float


@dataclass
class PortfolioData:
    portfolio_id: str
    name: str
    assets: list[PortfolioAsset]
