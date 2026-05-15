from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from stega_contracts.portfolio import (
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
)
from stega_core import Aggregate

if TYPE_CHECKING:
    from stega_portfolio.domain.command import CreatePortfolio


class PortfolioAsset:
    def __init__(
        self,
        symbol: str,
        weight: float,
        portfolio_id: str | None = None,
    ) -> None:
        self.symbol = symbol
        self.weight = weight
        self.portfolio_id = portfolio_id

    @classmethod
    def from_dict(cls, portfolio_id: str, assets: dict[str, float]) -> list[PortfolioAsset]:
        return [cls(symbol=symbol, weight=weight, portfolio_id=portfolio_id) for symbol, weight in assets.items()]


class Portfolio(Aggregate):
    __id_attr__: ClassVar[str] = "portfolio_id"

    def __init__(
        self,
        portfolio_id: str,
        name: str,
        assets: list[PortfolioAsset],
        version_number: int = 0,
    ) -> None:
        super().__init__(version_number)
        self.portfolio_id = portfolio_id
        self.name = name
        self.assets = assets
        event = PortfolioCreated(
            portfolio_id=self.portfolio_id,
            name=self.name,
            assets=self.assets,
        )
        self.record(event)

    def purge(self) -> None:
        self.assets.clear()
        self.record(PortfolioDeleted(self.portfolio_id))

    def update(self, name: str, assets: list[PortfolioAsset]) -> None:
        self.name = name
        self.assets = assets
        self.record(PortfolioUpdated(self.portfolio_id))

    @classmethod
    def from_command(cls, cmd: CreatePortfolio) -> Portfolio:
        assets = PortfolioAsset.from_dict(cmd.portfolio_id, cmd.assets)
        return cls(portfolio_id=cmd.portfolio_id, name=cmd.name, assets=assets)
