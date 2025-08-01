"""Abstract base class for portfolio repositories."""

import abc

from stega_portfolio.domain.portfolio import Portfolio


class AbstractPortfolioRepository(abc.ABC):
    """Abstract base class for portfolio repositories."""

    def __init__(self) -> None:
        """Initialize the AbstractPortfolioRepository."""
        self.seen: set[Portfolio] = set()

    def add(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the repository.

        Args:
            portfolio (Portfolio): The portfolio to add.

        """
        self._add(portfolio)
        self.seen.add(portfolio)

    def get(
        self,
        id: str,  # noqa: A002
    ) -> Portfolio | None:
        """Get a portfolio by its ID.

        Args:
            id (str): The unique UUIDv7 id of the portfolio to retrieve.

        Returns:
            Portfolio: The portfolio with the specified ID, or None if not found.

        """
        portfolio = self._get(id)
        if portfolio:
            self.seen.add(portfolio)
        return portfolio

    def delete(self, portfolio: Portfolio) -> None:
        """Delete a portfolio.

        Args:
            portfolio (Portfolio): The portfolio to delete.

        """
        self._delete(portfolio)
        self.seen.add(portfolio)

    @abc.abstractmethod
    def _add(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the repository.

        Args:
            portfolio (Portfolio): The portfolio to add.

        """
        err_msg = "_add method not implemented."
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def _get(
        self,
        id: str,  # noqa: A002
    ) -> Portfolio | None:
        """Get a portfolio by its ID.

        Args:
            id (str): The unique UUIDv7 id of the portfolio to retrieve.

        Returns:
            Portfolio: The portfolio with the specified ID, or None if not found.

        """
        err_msg = "_get method not implemented."
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def _delete(self, portfolio: Portfolio) -> None:
        """Delete a portfolio.

        Args:
            portfolio (Portfolio): The portfolio to delete.

        """
        err_msg = "_delete method not implemented."
        raise NotImplementedError(err_msg)
