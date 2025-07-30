"""Unit test fixtures for the stega_portfolio application."""

import typing as T

import pytest
from stega_portfolio.bootstrap import bootstrap
from stega_portfolio.domain.portfolio import Portfolio
from stega_portfolio.ports.repos.base import AbstractPortfolioRepository
from stega_portfolio.services.messagebus import MessageBus
from stega_portfolio.services.uow.base import AbstractUnitOfWork


class InMemoryPortfolioRepository(AbstractPortfolioRepository):
    """In-memory implementation of the portfolio repository for testing."""

    def __init__(
        self,
        portfolios: list[Portfolio] | None = None,
    ) -> None:
        """Initialize an InMemoryPortfolioRepository."""
        if portfolios is None:
            portfolios = []
        self._portfolios = portfolios
        super().__init__()

    def add_portfolio(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the in-memory repository."""
        self._portfolios.append(portfolio)

    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name."""
        for portfolio in self._portfolios:
            if portfolio.name == name:
                return portfolio
        err_msg = f"Portfolio with name '{name}' not found."
        raise KeyError(err_msg)


class InMemoryUnitOfWork(AbstractUnitOfWork):
    """In-memory implementation of the unit of work for testing."""

    def __enter__(self) -> T.Self:
        """Enter the unit of work context."""
        self.portfolios = InMemoryPortfolioRepository(portfolios=[])
        self.committed = False
        return super().__enter__()

    def commit(self) -> None:
        """Commit the unit of work."""
        self.committed = True

    def rollback(self) -> None:
        """Rollback the unit of work."""


@pytest.fixture
def unit_test_bus() -> MessageBus:
    """Fixture for creating a unit test message bus."""
    return bootstrap(uow=InMemoryUnitOfWork(), start_orm=False)
