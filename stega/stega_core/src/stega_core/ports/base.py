"""Abstract base class for stega core service ports."""

import abc

from stega_core.config import create_config, create_logger
from stega_core.domain.portfolio import PortfolioData


class PortfolioServicePort(abc.ABC):
    """Abstract base class for portfolio services."""

    def __init__(self) -> None:
        """Initialize the portfolio service port."""
        self.config = create_config()
        self.logger = create_logger(self.config)

    @abc.abstractmethod
    def create(self, portfolio: PortfolioData) -> str:
        """Create a new portfolio.

        Args:
            portfolio (PortfolioData): The portfolio to create.

        Returns:
            str: The ID of the newly created portfolio.

        """
        err_msg = "create method not implemented"
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def get(
        self,
        id: str,  # noqa: A002
    ) -> PortfolioData:
        """Get a portfolio by its unique ID.

        Args:
            id (str): The unique ID of the portfolio.

        Returns:
            PortfolioData: The portfolio with the specified ID.

        """
        err_msg = "get method not implemented"
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def update(
        self,
        id: str,  # noqa: A002
        portfolio: PortfolioData,
    ) -> None:
        """Update an existing portfolio.

        Args:
            id (str): The unique ID of the portfolio to update.
            portfolio (PortfolioData): The portfolio data to update.

        """
        err_msg = "update method not implemented"
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def delete(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Delete a portfolio by its unique ID.

        Args:
            id (str): The unique ID of the portfolio to delete.

        """
        err_msg = "delete method not implemented"
        raise NotImplementedError(err_msg)


ServiceType = PortfolioServicePort
