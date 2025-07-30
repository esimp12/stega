"""Service handler implementations for stega portfolio."""

from stega_portfolio.domain.commands import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_portfolio.domain.errors import ConflictError, ResourceNotFoundError
from stega_portfolio.domain.portfolio import Portfolio, PortfolioAsset
from stega_portfolio.services.uow.base import AbstractUnitOfWork


def create_portfolio(cmd: CreatePortfolio, uow: AbstractUnitOfWork) -> None:
    """Create a portfolio with the given name and assets.

    Args:
        cmd (CreatePortfolio): The command containing the portfolio name and assets.
        uow (AbstractUnitOfWork): The unit of work to manage the database session.

    Raises:
        ConflictError: If a portfolio with the same ID already exists.

    """
    with uow:
        portfolio = Portfolio.from_command(cmd)
        if uow.portfolios.get(cmd.id) is not None:
            err_msg = f"Portfolio with ID {cmd.id} already exists."
            raise ConflictError(err_msg)
        uow.portfolios.add(portfolio)
        uow.commit()


def delete_portfolio(cmd: DeletePortfolio, uow: AbstractUnitOfWork) -> None:
    """Delete a portfolio by its ID.

    Args:
        cmd (DeletePortfolio): The command containing the portfolio ID to delete.
        uow (AbstractUnitOfWork): The unit of work to manage the database session.

    Raises:
        ResourceNotFoundError: If the portfolio with the given ID does not exist.

    """
    with uow:
        portfolio = uow.portfolios.get(cmd.id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.id} does not exist."
            raise ResourceNotFoundError(err_msg)
        portfolio.deallocate()
        uow.portfolios.delete(portfolio)
        uow.commit()


def update_portfolio(cmd: UpdatePortfolio, uow: AbstractUnitOfWork) -> None:
    """Update an existing portfolio with new name and assets.

    Args:
        cmd (UpdatePortfolio): The command containing the portfolio ID, new name, and assets.
        uow (AbstractUnitOfWork): The unit of work to manage the database session.

    """
    with uow:
        portfolio = uow.portfolios.get(cmd.id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.id} does not exist."
            raise ResourceNotFoundError(err_msg)
        portfolio.update(
            name=cmd.name,
            assets=PortfolioAsset.from_dict(portfolio.id, cmd.assets),
        )
        uow.portfolios.add(portfolio)
        uow.commit()
