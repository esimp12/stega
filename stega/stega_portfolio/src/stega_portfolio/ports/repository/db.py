from stega_core import SqlAlchemyRepository

from stega_portfolio.domain.portfolio import Portfolio
from stega_portfolio.ports.repository.base import PortfolioRepository


class SqlAlchemyPortfolioRepository(SqlAlchemyRepository[Portfolio], PortfolioRepository):
    model = Portfolio
