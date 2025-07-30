"""Commands for the stega core service."""

from dataclasses import dataclass

from stega_lib.domain import Command


@dataclass
class CreatePortfolio(Command):
    """Command to create a portfolio.

    Attributes:
        name (str): The name of the portfolio.
        assets (Mapping[str, float]): A mapping of asset ids to their
            respective weights in the portfolio.

    """

    name: str
    assets: dict[str, float]


@dataclass
class DeletePortfolio(Command):
    """Command to delete a portfolio.

    Attributes:
        id (str): The unique UUIDv7 id of the portfolio to delete.

    """

    id: str


@dataclass
class UpdatePortfolio(Command):
    """Command to update a portfolio.

    Attributes:
        id (str): The unique UUIDv7 id of the portfolio to update.
        name (str): The new name of the portfolio.
        assets (Mapping[str, float]): A mapping of asset ids to their
            respective weights in the portfolio.

    """

    id: str
    name: str
    assets: dict[str, float]
