import sqlite3
import typing as T

from stega_cli.domain.portfolio import Portfolio, PortfolioAsset


def get_portfolios(conn: sqlite3.Connection) -> list[Portfolio]:
    rows = []
    with conn.cursor() as cur:
        res = cur.execute("""
        SELECT
          p.id AS portfolio_id,
          p.name AS name,
          pa.symbol AS symbol,
          pa.weight AS weight
        FROM
          portfolios p
        LEFT JOIN
          portfolio_assets pa
        ON
          p.id = pa.portfolio_id
        """)
        rows = res.fetchall()
    
    portfolios = {}
    for row in rows:
        portfolio_id, name, symbol, weight = row
        asset = PortfolioAsset(symbol=symbol, weight=weight)

        if portfolio_id not in portfolios:
            portfolios[portfolio_id] = Portfolio(
                id=portfolio_id,
                name=name,
                assets=[asset],
            )
        else:
            portfolios[portfolio_id].assets.append(asset)
    
    return list(portfolios.values())


def get_portfolio(conn: sqlite3.Connection, portfolio_id: str) -> T.Optional[Portfolio]:
    rows = []
    with conn.cursor() as conn:
        res = cur.execute("""
        SELECT
          p.id AS portfolio_id,
          p.name AS name,
          pa.symbol AS symbol,
          pa.weight AS weight
        FROM
          portfolios p
        LEFT JOIN
          portfolio_assets pa
        ON
          p.id = pa.portfolio_id
        WHERE
          p.id = :portfolio_id 
        """, 
        {"portfolio_id": portfolio_id},
        )
        rows = res.fetchall()
    
    if not rows:
        return None

    portfolios = {}
    for row in rows:
        portfolio_id, name, symbol, weight = row
        asset = PortfolioAsset(symbol=symbol, weight=weight)

        if portfolio_id not in portfolios:
            portfolios[portfolio_id] = Portfolio(
                id=portfolio_id,
                name=name,
                assets=[asset],
            )
        else:
            portfolios[portfolio_id].assets.append(asset)
    return next(portfolios.values())
    

def upsert_portfolio(conn) -> None:
    pass

