import sqlite3

from stega_cli.domain.portfolio import Portfolio, PortfolioAsset


def get_portfolios(conn: sqlite3.Connection) -> list[Portfolio]:
    cursor = conn.cursor()
    res = cursor.execute("""
    SELECT
      p.portfolio_id AS portfolio_id,
      p.name AS name,
      pa.symbol AS symbol,
      pa.weight AS weight
    FROM
      portfolios p
    LEFT JOIN
      portfolio_assets pa
    ON
      p.portfolio_id = pa.portfolio_id
    """)
    rows = res.fetchall()

    portfolios = {}
    for row in rows:
        portfolio_id, name, symbol, weight = row
        asset = PortfolioAsset(symbol=symbol, weight=weight)

        if portfolio_id not in portfolios:
            portfolios[portfolio_id] = Portfolio(
                portfolio_id=portfolio_id,
                name=name,
                assets=[asset],
            )
        else:
            portfolios[portfolio_id].assets.append(asset)

    return list(portfolios.values())


def get_portfolio(conn: sqlite3.Connection, portfolio_id: str) -> Portfolio | None:
    cursor = conn.cursor()
    res = cursor.execute(
        """
    SELECT
      p.portfolio_id AS portfolio_id,
      p.name AS name,
      pa.symbol AS symbol,
      pa.weight AS weight
    FROM
      portfolios p
    LEFT JOIN
      portfolio_assets pa
    ON
      p.portfolio_id = pa.portfolio_id
    WHERE
      p.portfolio_id = :portfolio_id 
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
                portfolio_id=portfolio_id,
                name=name,
                assets=[asset],
            )
        else:
            portfolios[portfolio_id].assets.append(asset)
    return next(portfolio for portfolio in portfolios.values())


def upsert_portfolio(
    conn: sqlite3.Connection,
    portfolio_id: str,
    name: str,
    assets: list[dict[str, str | float]],
) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO portfolios (portfolio_id, name) VALUES(:portfolio_id, :name) 
    """,
        {"portfolio_id": portfolio_id, "name": name},
    )
    asset_rows = [
        {
            "portfolio_id": portfolio_id,
            "symbol": asset["symbol"],
            "weight": asset["weight"],
        }
        for asset in assets
    ]
    cursor.executemany(
        """
    INSERT INTO portfolio_assets (portfolio_id, symbol, weight) VALUES(:portfolio_id, :symbol, :weight)
    """,
        asset_rows,
    )
