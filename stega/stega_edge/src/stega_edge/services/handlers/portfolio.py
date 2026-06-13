from stega_core import QueryResponse, QueryStatus

from stega_contracts.portfolio.command import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_contracts.portfolio.port import PortfolioServicePort
from stega_contracts.portfolio.query import GetPortfolio, ListPortfolios
from stega_contracts.portfolio.view import PortfolioListView, PortfolioView


async def get_portfolio(query: GetPortfolio, service: PortfolioServicePort) -> QueryResponse[PortfolioView]:
    async with service:
        service_result = await service.forward(query)
        return QueryResponse(
            status=QueryStatus.OK,
            result=service_result.result,
        )


async def list_portfolios(query: ListPortfolios, service: PortfolioServicePort) -> PortfolioListView:
    async with service:
        service_result = await service.forward(query)
        return QueryResponse(
            status=QueryStatus.OK,
            result=service_result.result,
        )


async def create_portfolio(cmd: CreatePortfolio, service: PortfolioServicePort) -> None:
    async with service:
        await service.forward(cmd)


async def update_portfolio(cmd: UpdatePortfolio, service: PortfolioServicePort) -> None:
    async with service:
        await service.forward(cmd)


async def delete_portfolio(cmd: DeletePortfolio, service: PortfolioServicePort) -> None:
    async with service:
        await service.forward(cmd)
