import typing_extensions as T

from src.db import DbConnArgs, acquire_connection
from src.portfolio.domain import Portfolio


class PostgreSqlPortfolioRepository:
    """Implementation of the PortfolioRepository interface for PostgreSQL."""

    def __init__(self, dbargs: DbConnArgs) -> None:
        """Initialize the PostgreSQL portfolio repository."""
        self.dbargs = dbargs

    def add_portfolio(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the PostgreSQL database.

        Args:
            portfolio (Portfolio): The portfolio to add.
        """
        self._add_assets(portfolio)
        all_assets = self._get_assets(list(portfolio.assets.keys()))
        asset_ids = {name: asset_id for asset_id, name in all_assets}

        portfolio_entries = [
            (portfolio.name, asset_ids[asset_name], asset_weight)
            for asset_name, asset_weight in portfolio.assets.items()
        ]
        with acquire_connection(self.dbargs) as conn:
            with conn.cursor() as cursor:
                cursor.executemany(
                    """INSERT INTO portfolios (name, asset_id, weight)
                    VALUES (%s, %s, %s)""",
                    portfolio_entries,
                )
                conn.commit()

    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name from the PostgreSQL database.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Portfolio: The portfolio with the specified name.

        Raises:
            ValueError: If the portfolio with the specified name does not exist.
        """
        with acquire_connection(self.dbargs) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT
                      p.id AS portfolio_id,
                      p.name AS portfolio_name,
                      a.name AS asset_name,
                      p.weight AS asset_weight
                    FROM
                      portfolios p
                    LEFT JOIN
                      assets a
                    ON
                      p.asset_id = a.id
                    WHERE
                      p.name = %s
                    """,
                    (name,),
                )
                rows = cursor.fetchall()
                if len(rows) == 0:
                    raise ValueError(f"Portfolio '{rows}' not found.")
                return _create_portfolio_from_rows(rows)

    def _add_assets(self, portfolio: Portfolio) -> None:
        asset_names = list(portfolio.assets.keys())
        known_assets = self._get_assets(asset_names)
        known_assets_names = [name for _, name in known_assets]
        asset_names_to_add = [
            name for name in asset_names if name not in known_assets_names
        ]
        with acquire_connection(self.dbargs) as conn:
            with conn.cursor() as cursor:
                cursor.executemany(
                    """INSERT INTO assets (name) VALUES (%s)""",
                    [(name,) for name in asset_names_to_add],
                )
                conn.commit()

    def _get_assets(self, asset_names: T.List[str]) -> T.List[T.Tuple[int, str]]:
        with acquire_connection(self.dbargs) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT
                      id, name
                    FROM
                      assets
                    WHERE
                      name IN %s
                    """,
                    (tuple(asset_names),),
                )
                return cursor.fetchall()


def _create_portfolio_from_rows(rows: T.List[T.Tuple]) -> Portfolio:
    assets = {}
    for _, _, asset_name, asset_weight in rows:
        if asset_name not in assets:
            assets[asset_name] = asset_weight
    return Portfolio(
        name=rows[0][1],
        assets=assets,
    )
