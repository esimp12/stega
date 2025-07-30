"""Object relational mapping definitions for domain entities."""

from sqlalchemy import (
    Column,
    Engine,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import registry, relationship

from stega_portfolio.domain.portfolio import Portfolio, PortfolioAsset

mapper_registry = registry()
metadata = mapper_registry.metadata

_PORTFOLIOS_TABLE = Table(
    "portfolios",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("name", String(255), nullable=False, unique=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)

_PORTFOLIO_ASSETS_TABLE = Table(
    "portfolio_assets",
    metadata,
    Column("portfolio_id", ForeignKey("portfolios.id"), primary_key=True, nullable=False),
    Column("symbol", String(10), primary_key=True, nullable=False),
    Column("weight", Float, nullable=False),
)


def get_engine(uri: str) -> Engine:
    """Create SQLAlchemy dialect specific engine.

    Args:
        uri: A string of the SQL database connection URI.

    Returns:
        A SQLAlchemy engine.

    """
    engine = create_engine(uri)
    metadata.create_all(engine)
    return engine


def start_mappers() -> None:
    """Create the relational mappings for aggregates and domain entities."""
    portfolio_asset_mapper = mapper_registry.map_imperatively(PortfolioAsset, _PORTFOLIO_ASSETS_TABLE)
    mapper_registry.map_imperatively(
        Portfolio,
        _PORTFOLIOS_TABLE,
        properties={
            "assets": relationship(portfolio_asset_mapper),
        },
    )
