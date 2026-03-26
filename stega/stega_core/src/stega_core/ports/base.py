"""Abstract base class for stega core service ports."""

import abc

from stega_core.config import create_config, create_logger
from stega_core.domain.portfolio import PortfolioData


class PortfolioServicePort(abc.ABC):
    """Abstract base class for portfolio services."""

    def __init__(self) -> None:
        self.config = create_config()
        self.logger = create_logger(self.config)

    @abc.abstractmethod
    def get(self, portfolio_id: str) -> PortfolioData:
        """Get a portfolio by its unique ID.

        Args:
            portfolio_id: A str of the unique ID of the portfolio.

        Returns:
            PortfolioData: The portfolio with the specified ID.

        """
        err_msg = "get method not implemented"
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def list(self) -> list[PortfolioData]:
        """Get all existing portfolios.

        Returns:
            A list of PortfolioData instances.

        """
        err_msg = "list method not implemented"
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def create(self, correlation_id: str, portfolio_data: PortfolioData) -> str:
        """Create a new portfolio.

        Args:
            correlation_id: A str of the globaly unique ID of a client event
                trace for this action.
            portfolio_data: A PortfolioData instance of the data to create the
                portfolio with.

        Returns:
            A str of the unique ID of the newly created portfolio.

        """
        err_msg = "create method not implemented"
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def update(self, correlation_id: str, portfolio_id: str, portfolio_data: PortfolioData) -> None:
        """Update an existing portfolio.

        Args:
            correlation_id: A str of the globaly unique ID of a client event
                trace for this action.
            portfolio_id: A str of the unique ID of the portfolio.
            portfolio_data: A PortfolioData instance of the data to update the
                portfolio with.

        """
        err_msg = "update method not implemented"
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def delete(self, correlation_id: str, portfolio_id: str) -> None:
        """Delete a portfolio by its unique ID.

        Args:
            correlation_id: A str of the globaly unique ID of a client event
                trace for this action.
            portfolio_id: A str of the unique ID of the portfolio.

        """
        err_msg = "delete method not implemented"
        raise NotImplementedError(err_msg)


ServiceType = PortfolioServicePort
