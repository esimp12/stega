"""Implementation of the PortfolioRepository interface for PostgreSQL."""

from sqlalchemy.orm import Session

from stega_portfolio.domain.portfolio import Portfolio
from stega_portfolio.ports.repos.base import AbstractPortfolioRepository


class SqlAlchemyPortfolioRepository(AbstractPortfolioRepository):
    """Implementation of the PortfolioRepository interface for PostgreSQL."""

    def __init__(self, session: Session) -> None:
        """Initialize the PostgreSQL portfolio repository."""
        super().__init__()
        self.session = session

    def _add(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the PostgreSQL database.

        Args:
            portfolio (Portfolio): The portfolio to add.

        """
        self.session.add(portfolio)

    def _get(
        self,
        id: str,  # noqa: A002
    ) -> Portfolio | None:
        """Get a portfolio by its ID from the PostgreSQL database.

        Args:
            id (str): The unique UUIDv7 id of the portfolio to retrieve.

        Returns:
            Portfolio: The portfolio with the specified ID, or None if not found.

        """
        return self.session.query(Portfolio).where(Portfolio.id == id).first()

    def _delete(
        self,
        portfolio: Portfolio,
    ) -> None:
        """Delete a portfolio by its ID from the PostgreSQL database.

        Args:
            portfolio (Portfolio): The portfolio to delete.

        """
        self.session.delete(portfolio)
