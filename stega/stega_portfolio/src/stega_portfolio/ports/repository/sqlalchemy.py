from stega_core import AbstractSqlAlchemyRepository

from stega_portfolio.domain.portfolio import Portfolio
from stega_portfolio.ports.repository.base import PortfolioRepository


class SqlAlchemyPortfolioRepository(AbstractSqlAlchemyRepository[Portfolio], PortfolioRepository):
    model = Portfolio
