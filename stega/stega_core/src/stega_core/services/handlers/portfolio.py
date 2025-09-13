"""Portfolio service module for creating and managing portfolios."""

from stega_core.domain.commands import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_core.domain.portfolio import PortfolioAsset, PortfolioData
from stega_core.ports.base import PortfolioServicePort


def create_portfolio(cmd: CreatePortfolio, service: PortfolioServicePort) -> str:
    """Create a new portfolio with the given name and assets.

    Args:
        cmd (CreatePortfolio): The command containing the portfolio details.
        service (PortfolioServicePort): The portfolio service to use for creating the portfolio.

    Returns:
        str: The ID of the newly created portfolio.

    """
    data = _create_portfolio_data(cmd.name, cmd.assets)
    return service.create(data)


def get_portfolio(
    id: str,  # noqa: A002
    service: PortfolioServicePort,
) -> PortfolioData:
    """Retrieve a portfolio by its ID.

    Args:
        id (str): The ID of the portfolio to retrieve.
        service (PortfolioServicePort): The portfolio service to use for retrieving the portfolio.

    Returns:
        PortfolioData: The portfolio data.

    """
    return service.get(id)


def update_portfolio(
    cmd: UpdatePortfolio,
    service: PortfolioServicePort,
) -> None:
    """Update an existing portfolio.

    Args:
        cmd (UpdatePortfolio): The command containing the portfolio details.
        service (PortfolioServicePort): The portfolio service to use for updating the portfolio.

    """
    data = _create_portfolio_data(cmd.name, cmd.assets)
    service.update(cmd.id, data)


def delete_portfolio(
    cmd: DeletePortfolio,
    service: PortfolioServicePort,
) -> None:
    """Delete a portfolio by its ID.

    Args:
        cmd (DeletePortfolio): The command containing the portfolio ID to delete.
        service (PortfolioServicePort): The portfolio service to use for deleting the portfolio.

    """
    service.delete(cmd.id)


def list_portfolios(service: PortfolioServicePort) -> list[PortfolioData]:
    """Get a list of all portfolios.

    Args:
        service (PortfolioServicePort): The portfolio service to use for retrieving the portfolio.

    Returns:
        list[PortfolioData]: A list of all portfolio data.

    """
    return service.list()
 

def _create_portfolio_data(
    name: str,
    assets: dict[str, float],
) -> PortfolioData:
    """Helper function to create PortfolioData from name and assets."""
    return PortfolioData(
        name=name,
        assets=[PortfolioAsset(symbol=asset_name, weight=amount) for asset_name, amount in assets.items()],
    )
