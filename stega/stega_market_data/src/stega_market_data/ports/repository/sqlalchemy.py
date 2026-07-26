from sqlalchemy import insert
from stega_core import AbstractSqlAlchemyRepository

from stega_market_data.domain.price import PricePull
from stega_market_data.ports.orm import price_table
from stega_market_data.ports.repository.base import PricePullRepository


class SqlAlchemyPricePullRepository(AbstractSqlAlchemyRepository[PricePull], PricePullRepository):
    model = PricePull

    async def _add(self, pull: PricePull) -> None:
        self._session.add(pull)
        if not pull.prices:
            return
        await self._session.flush()
        await self._session.execute(
            insert(price_table),
            [
                {
                    "pull_id": pull.pull_id,
                    "ticker": price.ticker,
                    "dt": price.dt,
                    "amount": price.amount,
                }
                for price in pull.prices
            ],
        )
