from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import registry, relationship

from stega_portfolio.domain.portfolio import Portfolio, PortfolioAsset

mapper_registry = registry()
metadata = mapper_registry.metadata

portfolio_table = Table(
    "portfolios",
    metadata,
    Column(
        "_id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    ),
    Column("portfolio_id", String, nullable=False, unique=True),
    Column("name", String, nullable=False, unique=True),
    Column("version_number", Integer, nullable=False, default=0),
)

asset_table = Table(
    "assets",
    metadata,
    Column(
        "_id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    ),
    Column(
        "portfolio_id",
        String,
        ForeignKey("portfolios.portfolio_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("symbol", String, nullable=False),
    Column("weight", Numeric, nullable=False),
    UniqueConstraint("portfolio_id", "symbol", name="uq_assets_portfolio_symbol"),
)


def init_metadata(db_uri: str) -> None:
    engine = create_engine(db_uri)
    metadata.create_all(engine)


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        PortfolioAsset,
        asset_table,
        properties={
            "portfolio_id": asset_table.c.portfolio_id,
            "symbol": asset_table.c.symbol,
            "weight": asset_table.c.weight,
        },
        primary_key=[asset_table.c.portfolio_id, asset_table.c.symbol],
    )
    mapper_registry.map_imperatively(
        Portfolio,
        portfolio_table,
        properties={
            "portfolio_id": portfolio_table.c.portfolio_id,
            "name": portfolio_table.c.name,
            "version_number": portfolio_table.c.version_number,
            "assets": relationship(
                PortfolioAsset,
                cascade="all, delete-orphan",
                passive_deletes=True,
            ),
        },
        primary_key=[portfolio_table.c.portfolio_id],
        version_id_col=portfolio_table.c.version_number,
    )
