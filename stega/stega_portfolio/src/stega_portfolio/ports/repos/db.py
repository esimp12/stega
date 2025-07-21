"""Implementation of the PortfolioRepository interface for PostgreSQL."""

from sqlalchemy.orm import Session

from stega_portfolio.domain.portfolio import Portfolio
from stega_portfolio.ports.repos.base import AbstractPortfolioRepository


class SqlAlchemyPortfolioRepository(AbstractPortfolioRepository):
    """Implementation of the PortfolioRepository interface for PostgreSQL."""

    def __init__(self, session: Session) -> None:
        """Initialize the PostgreSQL portfolio repository."""
        self.session = session

    def add_portfolio(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the PostgreSQL database.

        Args:
            portfolio (Portfolio): The portfolio to add.

        """
        self.session.add(portfolio)

    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name from the PostgreSQL database.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Portfolio: The portfolio with the specified name.

        Raises:
            ValueError: If the portfolio with the specified name does not exist.

        """
        res = self.session.query(Portfolio).first()
        if res is None:
            err_msg = f"Portfolio '{name}' not found."
            raise ValueError(err_msg)
        return res
