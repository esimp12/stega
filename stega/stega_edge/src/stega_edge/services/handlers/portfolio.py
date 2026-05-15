from collections.abc import Awaitable

from stega_edge.domain.command import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_edge.domain.portfolio import PortfolioAsset, PortfolioData
from stega_edge.domain.query import GetPortfolio, ListPortfolios
from stega_edge.ports.base import PortfolioServicePort


async def create_portfolio(cmd: CreatePortfolio, service: PortfolioServicePort) -> Awaitable[None]:
    data = _create_portfolio_data(cmd.name, cmd.assets)
    await service.create(cmd.correlation_id, data)


async def get_portfolio(query: GetPortfolio, service: PortfolioServicePort) -> Awaitable[PortfolioData]:
    return await service.get(query.portfolio_id)


async def update_portfolio(cmd: UpdatePortfolio, service: PortfolioServicePort) -> Awaitable[None]:
    data = _create_portfolio_data(cmd.name, cmd.assets)
    await service.update(cmd.id, data)


async def delete_portfolio(cmd: DeletePortfolio, service: PortfolioServicePort) -> Awaitable[None]:
    await service.delete(cmd.id)


async def list_portfolios(_: ListPortfolios, service: PortfolioServicePort) -> Awaitable[list[PortfolioData]]:
    return await service.list()


def _create_portfolio_data(name: str, assets: dict[str, float]) -> PortfolioData:
    return PortfolioData(
        name=name,
        assets=[PortfolioAsset(symbol=asset_name, weight=amount) for asset_name, amount in assets.items()],
    )
