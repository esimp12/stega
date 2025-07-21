
import pytest
from stega_portfolio.bootstrap import bootstrap
from stega_portfolio.domain.portfolio import Portfolio
from stega_portfolio.ports.repos.base import AbstractPortfolioRepository
from stega_portfolio.services.messagebus import MessageBus
from stega_portfolio.services.uow.base import AbstractUnitOfWork


class InMemoryPortfolioRepository(AbstractPortfolioRepository):
    def __init__(
        self,
        portfolios: list[Portfolio] | None = None,
    ):
        if portfolios is None:
            portfolios = []
        self._portfolios = portfolios
        super().__init__()

    def add_portfolio(self, portfolio: Portfolio):
        self._portfolios.append(portfolio)

    def get_portfolio(self, name: str) -> Portfolio:
        for portfolio in self._portfolios:
            if portfolio.name == name:
                return portfolio
        raise KeyError(f"Portfolio with name '{name}' not found.")


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __enter__(self):
        self.portfolios = InMemoryPortfolioRepository(portfolios=[])
        self.committed = False
        return super().__enter__()

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


@pytest.fixture
def unit_test_bus() -> MessageBus:
    return bootstrap(uow=InMemoryUnitOfWork(), start_orm=False)
