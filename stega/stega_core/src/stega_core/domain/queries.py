"""Queries for the stega core service."""

from dataclasses import dataclass

from stega_lib.domain import Query


@dataclass
class GetPorftolio(Query):
    """Query to fetch a portfolio.

    Attributes:
        portfolio_id (str): The unique id of the portfolio.

    """

    portfolio_id: str


@dataclass
class ListPortfolios(Query):
    """Query to list all portfolios."""
