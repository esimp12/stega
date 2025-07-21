"""Abstract base class for portfolio repositories."""

import abc

from stega_portfolio.domain.portfolio import Portfolio


class AbstractPortfolioRepository(abc.ABC):
    """Abstract base class for portfolio repositories."""

    @abc.abstractmethod
    def add_portfolio(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the repository.

        Args:
            portfolio (Portfolio): The portfolio to add.

        """
        err_msg = "add_portfolio method not implemented."
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Portfolio: The portfolio with the specified name.

        """
        err_msg = "get_portfolio method not implemented."
        raise NotImplementedError(err_msg)
