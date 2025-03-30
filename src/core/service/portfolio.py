import typing_extensions as T

from src.core.domain.portfolio import Portfolio


def create_portfolio(name: str, assets: T.Mapping[str, float]) -> Portfolio:
    """Create a portfolio with the given name and assets.

    Args:
        name (str): The name of the portfolio.
        assets (Mapping[str, float]): A mapping of stock symbols to their
            respective weights in the portfolio.

    Returns:
        Portfolio: A Portfolio object with the specified name and assets.
    """

    return Portfolio(name=name, assets=assets)
