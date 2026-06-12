from dataclasses import dataclass
from typing import ClassVar, TypedDict

from stega_core import Event


class AssetAllocation(TypedDict):
    symbol: str
    weight: float


@dataclass(frozen=True, kw_only=True)
class PortfolioCreated(Event):
    topic: ClassVar[str] = "portfolio_created"
    portfolio_id: str
    name: str
    assets: list[AssetAllocation]


@dataclass(frozen=True, kw_only=True)
class PortfolioDeleted(Event):
    topic: ClassVar[str] = "portfolio_deleted"
    portfolio_id: str


@dataclass(frozen=True, kw_only=True)
class PortfolioUpdated(Event):
    topic: ClassVar[str] = "portfolio_updated"
    portfolio_id: str
