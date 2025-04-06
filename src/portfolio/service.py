import typing_extensions as T

from config import PORTFOLIO_CONFIG as config
from src.portfolio.domain import Portfolio
from src.portfolio.ports.base import PortfolioRepository


def create_portfolio(name: str, assets: T.Mapping[str, float]) -> Portfolio:
    """Create a portfolio with the given name and assets.

    Args:
        name (str): The name of the portfolio.
        assets (Mapping[str, float]): A mapping of stock symbols to their
            respective weights in the portfolio.

    Returns:
        Portfolio: A Portfolio object with the specified name and assets.
    """
    repo = PortfolioRepository.create_repo(
        repo_type_str=config.STEGA_PORTFOLIO_REPO_TYPE,
        config=config,
    )
    portfolio = Portfolio(name=name, assets=assets)
    repo.add_portfolio(portfolio)
    return portfolio
