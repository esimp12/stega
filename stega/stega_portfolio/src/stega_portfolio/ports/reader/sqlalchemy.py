from collections import defaultdict

from sqlalchemy import Row, text
from stega_core import AbstractSqlAlchemyReader

from stega_portfolio.domain.view import AssetView, PortfolioListView, PortfolioView
from stega_portfolio.ports.reader.base import PortfolioReader


class SqlAlchemyPortfolioReader(AbstractSqlAlchemyReader, PortfolioReader):
    async def get(self, portfolio_id: str) -> PortfolioView | None:
        stmt = text(
            """
            SELECT
              p.portfolio_id,
              p.name,
              a.symbol,
              a.weight
            FROM
              portfolios p
            LEFT JOIN
              assets a
            ON
              p.portfolio_id = a.portfolio_id
            WHERE
              p.portfolio_id = :portfolio_id
            """
        )
        result = await self._session.execute(stmt, {"portfolio_id": portfolio_id})
        rows = result.all()
        portfolios = _get_portfolios(rows)
        portfolio_keys = list(portfolios.keys())
        if len(portfolio_keys) == 0:
            return None

        portfolio_id, name = portfolio_keys[0]
        assets = portfolios[(portfolio_id, name)]

        return PortfolioView(
            portfolio_id=portfolio_id,
            name=name,
            assets=[AssetView(symbol=symbol, weight=weight) for symbol, weight in assets],
        )

    async def list(self) -> PortfolioListView:
        stmt = text(
            """
            SELECT
              p.portfolio_id,
              p.name,
              a.symbol,
              a.weight
            FROM
              portfolios p
            LEFT JOIN
              assets a
            ON
              p.portfolio_id = a.portfolio_id
            """
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        portfolios = _get_portfolios(rows)
        views = [
            PortfolioView(
                portfolio_id=portfolio_id,
                name=name,
                assets=[AssetView(symbol=symbol, weight=weight) for symbol, weight in assets],
            )
            for (portfolio_id, name), assets in portfolios.items()
        ]
        return PortfolioListView(portfolios=views)


type _Row = Row[tuple[str, str, str, float]]
type _Portfolio = tuple[str, str]
type _Asset = tuple[str, float]


def _get_portfolios(rows: list[_Row]) -> dict[_Portfolio, list[_Asset]]:
    portfolios = defaultdict(list)
    for row in rows:
        id_tuple = (row.portfolio_id, row.name)
        asset_tuple = (row.symbol, row.weight)
        portfolios[id_tuple].append(asset_tuple)
    return dict(portfolios)
