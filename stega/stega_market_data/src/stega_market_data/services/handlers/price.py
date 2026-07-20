from stega_core import AbstractUnitOfWork
from stega_contracts.market_data.command import PullPrices
from stega_market_data.domain.price import PricePull
from stega_market_data.ports.repository.base import PricePullRepository


async def pull_prices(cmd: PullPrices, uow: AbstractUnitOfWork, provider: PriceProvider) -> None:
    results = await provider.fetch(cmd.kind, cmd.tickers)
    async with uow:
        repo = uow.repo(PricePullRepository)
        pull = PricePull.open()
        for result in results:
            pull.record_result(result)
        await repo.add(pull)
        uow.commit()
