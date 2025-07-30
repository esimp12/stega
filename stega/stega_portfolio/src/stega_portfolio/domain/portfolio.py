"""Portfolio domain model for the stega portfolio service."""

import typing as T

from stega_lib.domain import Aggregate
from stega_lib.events import PortfolioCreated, PortfolioDeleted, PortfolioUpdated

from stega_portfolio.domain.commands import CreatePortfolio


class PortfolioAsset:
    """Asset class to represent a stock in the portfolio.

    Attributes:
        symbol (str): The stock symbol. Uniquely identifies the stock in the portfolio.
        weight (float): The weight of the stock in the portfolio.
        portfolio_id (Optional[str]): The ID of the portfolio this asset belongs to.

    """

    def __init__(
        self,
        symbol: str,
        weight: float,
        portfolio_id: str | None = None,
    ) -> None:
        """Initialize a PortfolioAsset instance."""
        self.symbol = symbol
        self.weight = weight
        self.portfolio_id = portfolio_id

    @classmethod
    def from_dict(cls, portfolio_id: str, assets: dict[str, float]) -> list[T.Self]:
        """Create a list of PortfolioAsset instances from a dictionary of assets.

        Args:
            portfolio_id (str): The ID of the portfolio this asset belongs to.
            assets (dict[str, float]): A dictionary mapping stock symbols to their weights.

        Returns:
            list[PortfolioAsset]: A list of PortfolioAsset instances.

        """
        return [cls(symbol=symbol, weight=weight, portfolio_id=portfolio_id) for symbol, weight in assets.items()]


class Portfolio(Aggregate):
    """Portfolio class to represent a portfolio of stocks.

    Attributes:
        id (str): The unique identifier for the portfolio.
        name (str): The name of the portfolio.
        assets (Mapping[str, float]): A mapping of asset ids to their
            respective weights in the portfolio.
        version_number (int): The version number of the portfolio aggregate.
        events (List[Event]): A list of events associated with the portfolio.

    """

    def __init__(
        self,
        id: str,  # noqa: A002
        name: str,
        assets: list[PortfolioAsset],
        version_number: int = 0,
    ) -> None:
        """Initialize a Portfolio instance."""
        super().__init__(id, version_number)
        self.name = name
        self.assets = assets
        self.events = []

    def allocate(self) -> None:
        """Allocate the portfolio so it can be used."""
        self.events.append(PortfolioCreated(self.id))

    def deallocate(self) -> None:
        """Deallocate the portfolio so it no longer exists along with its asset composition."""
        self.assets.clear()
        self.events.append(PortfolioDeleted(self.id))

    def update(self, name: str, assets: list[PortfolioAsset]) -> None:
        """Update the portfolio with a new name and assets.

        Args:
            name (str): The new name for the portfolio.
            assets (list[PortfolioAsset]): The new list of assets for the portfolio.

        """
        self.name = name
        self.assets = assets
        self.events.append(PortfolioUpdated(self.id))

    @classmethod
    def from_command(cls, cmd: CreatePortfolio) -> T.Self:
        """Create a Portfolio instance from a CreatePortfolio command.

        Args:
            cmd (CreatePortfolio): The command containing the portfolio name and assets.

        Returns:
            Portfolio: A Portfolio object with the specified name and assets.

        """
        assets = PortfolioAsset.from_dict(cmd.id, cmd.assets)
        portfolio = cls(id=cmd.id, name=cmd.name, assets=assets)
        portfolio.allocate()
        return portfolio
