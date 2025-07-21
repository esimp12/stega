"""Command data structures for the stega_portfolio domain."""

import typing as T
from dataclasses import dataclass

from stega_lib.domain import Command


@dataclass
class CreatePortfolio(Command):
    """Command to create a portfolio.

    Attributes:
        id (str): The unique UUIDv7 id of the portfolio to create.
        name (str): The name of the portfolio.
        assets (Mapping[str, float]): A mapping of asset ids to their
            respective weights in the portfolio.

    """

    id: str
    name: str
    assets: T.Mapping[str, float]
