import typing_extensions as T

from stega_core.domain.portfolio import Portfolio


class PortfolioRepository(T.Protocol):
    """Abstract base class for portfolio repositories."""

    def add_portfolio(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the repository.

        Args:
            portfolio (Portfolio): The portfolio to add.

        """
        raise NotImplementedError

    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Portfolio: The portfolio with the specified name.

        """
        raise NotImplementedError
