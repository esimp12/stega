from stega_core import (
    AbstractUnitOfWork,
)

from stega_portfolio.domain.command import (
    CreatePortfolio,
    DeletePortfolio,
    UpdatePortfolio,
)
from stega_portfolio.domain.error import ConflictError, ResourceNotFoundError
from stega_portfolio.domain.portfolio import Portfolio, PortfolioAsset
from stega_portfolio.ports.repository.base import PortfolioRepository


async def get_portfolio(query: GetPortfolio, qc: QueryContext) -> None:
    async with qc:
        queries = qc.query(PortfolioQueries)
        return await queries.get(query.portfolio_id)


async def create_portfolio(cmd: CreatePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)
        if repo.get(cmd.portfolio_id) is not None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} already exists."
            raise ConflictError(err_msg)

        portfolio = Portfolio.from_command(cmd)
        repo.add(portfolio)
        uow.commit()


async def delete_portfolio(cmd: DeletePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)

        portfolio = repo.get(cmd.portfolio_id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} does not exist."
            raise ResourceNotFoundError(err_msg)

        portfolio.purge()
        repo.delete(portfolio)
        uow.commit()


async def update_portfolio(cmd: UpdatePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)

        portfolio = repo.get(cmd.portfolio_id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} does not exist."
            raise ResourceNotFoundError(err_msg)

        portfolio.update(
            name=cmd.name,
            assets=PortfolioAsset.from_dict(portfolio.portfolio_id, cmd.assets),
        )
        repo.update(portfolio)
        uow.commit()
