"""Service handler implementations for stega portfolio."""

from stega_portfolio.domain.commands import CreatePortfolio
from stega_portfolio.domain.portfolio import Portfolio
from stega_portfolio.services.uow.base import AbstractUnitOfWork


def create_portfolio(cmd: CreatePortfolio, uow: AbstractUnitOfWork) -> None:
    """Create a portfolio with the given name and assets.

    Args:
        cmd (CreatePortfolio): The command containing the portfolio name and assets.
        uow (AbstractUnitOfWork): The unit of work to manage the database session.

    """
    with uow:
        portfolio = Portfolio.from_command(cmd)
        uow.portfolios.add_portfolio(portfolio)
        uow.commit()
