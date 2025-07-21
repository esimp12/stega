"""Portfolio domain model for the stega portfolio service."""

import typing as T

from stega_lib.domain import Aggregate, DomainEntity

from stega_portfolio.domain.commands import CreatePortfolio


class PortfolioAsset(DomainEntity):
    """Asset class to represent a stock in the portfolio.

    Attributes:
        symbol (str): The stock symbol.
        weight (float): The weight of the stock in the portfolio.
        id (Optional[int]): The unique identifier for the asset.

    """

    def __init__(
        self,
        symbol: str,
        weight: float,
        id: str | None = None,  # noqa: A002
    ) -> None:
        """Initialize a PortfolioAsset instance."""
        super().__init__(id)
        self.symbol = symbol
        self.weight = weight


class Portfolio(Aggregate):
    """Portfolio class to represent a portfolio of stocks.

    Attributes:
        name (str): The name of the portfolio.
        assets (Mapping[str, float]): A mapping of asset ids to their
            respective weights in the portfolio.
        id (Optional[str]): The unique identifier for the portfolio.
        version_number (int): The version number of the portfolio aggregate.

    """

    def __init__(
        self,
        name: str,
        assets: T.Sequence[PortfolioAsset],
        id: str | None = None,  # noqa: A002
        version_number: int = 0,
    ) -> None:
        """Initialize a Portfolio instance."""
        super().__init__(id, version_number)
        self.name = name
        self.assets = assets

    @classmethod
    def from_command(cls, cmd: CreatePortfolio) -> T.Self:
        """Create a Portfolio instance from a CreatePortfolio command.

        Args:
            cmd (CreatePortfolio): The command containing the portfolio name and assets.

        Returns:
            Portfolio: A Portfolio object with the specified name and assets.

        """
        assets = [PortfolioAsset(symbol=symbol, weight=weight) for symbol, weight in cmd.assets.items()]
        return cls(name=cmd.name, assets=assets, id=cmd.id)
