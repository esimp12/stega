from dataclasses import dataclass


@dataclass
class PortfolioAsset:
    symbol: str
    weight: float


@dataclass
class Portfolio:
    id: str
    name: str
    assets: list[PortfolioAsset]

