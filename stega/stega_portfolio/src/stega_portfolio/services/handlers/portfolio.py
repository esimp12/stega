from stega_core import (
    AbstractQueryContext,
    AbstractUnitOfWork,
    ConflictError,
    QueryResponse,
    QueryStatus,
    ResourceNotFoundError,
)

from stega_portfolio.domain.command import (
    CreatePortfolio,
    DeletePortfolio,
    UpdatePortfolio,
)
from stega_portfolio.domain.portfolio import Portfolio, PortfolioAsset
from stega_portfolio.domain.query import GetPortfolio, ListPortfolios
from stega_portfolio.domain.view import PortfolioListView, PortfolioView
from stega_portfolio.ports.reader.base import PortfolioReader
from stega_portfolio.ports.repository.base import PortfolioRepository


async def get_portfolio(
    query: GetPortfolio,
    qc: AbstractQueryContext,
) -> QueryResponse[PortfolioView]:
    async with qc:
        reader = qc.reader(PortfolioReader)
        view = await reader.get(query.portfolio_id)
        return QueryResponse(
            status=QueryStatus.OK,
            result=view,
        )


async def list_portfolios(
    _: ListPortfolios,
    qc: AbstractQueryContext,
) -> QueryResponse[PortfolioListView]:
    async with qc:
        reader = qc.reader(PortfolioReader)
        view = await reader.list()
        return QueryResponse(
            status=QueryStatus.OK,
            result=view,
        )


async def create_portfolio(cmd: CreatePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)
        existing = await repo.get(cmd.portfolio_id)
        if existing is not None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} already exists."
            raise ConflictError(err_msg)

        portfolio = Portfolio.from_command(cmd)
        await repo.add(portfolio)
        await uow.commit()


async def delete_portfolio(cmd: DeletePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)

        portfolio = await repo.get(cmd.portfolio_id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} does not exist."
            raise ResourceNotFoundError(err_msg)

        portfolio.purge()
        await repo.delete(portfolio)
        await uow.commit()


async def update_portfolio(cmd: UpdatePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)

        portfolio = await repo.get(cmd.portfolio_id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} does not exist."
            raise ResourceNotFoundError(err_msg)

        assets = None
        if cmd.assets is not None:
            assets = PortfolioAsset.from_dict(portfolio.portfolio_id, cmd.assets)
        portfolio.update(name=cmd.name, assets=assets)
        await repo.update(portfolio)
        await uow.commit()
