from sqlalchemy import (
    BigInteger,
    Column,
    Datetime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy import (
    Enum as SqlAlchemyEnum,
)
from sqlalchemy.orm import registry
from stega_contracts.market_data.command import PullKind

from stega_market_data.domain.price import PricePull, PullStatus

mapper_registry = registry()
metadata = mapper_registry.metadata


pull_table = Table(
    "price_pulls",
    metadata,
    Column(
        "_id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    ),
    Column("pull_id", String, nullable=False, unique=True),
    Column("kind", SqlAlchemyEnum(PullKind), nullable=False),
    Column("status", SqlAlchemyEnum(PullStatus), nullable=False),
    Column("version_number", Integer, nullable=False, default=0),
)

price_table = Table(
    "prices",
    metadata,
    Column(
        "_id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    ),
    Column("pull_id", String, ForeignKey("price_pulls.pull_id", ondelete="CASCADE"), nullable=False),
    Column("ticker", String, nullable=False),
    Column("dt", Datetime, nullable=False),
    Column("amount", Numeric, nullable=False),
    UniqueConstraint("ticker", "dt", name="uq_prices_ticker_dt"),
    Index("ix_prices_ticker_dt", "ticker", "dt"),
)


def init_metadata(db_uri: str) -> None:
    engine = create_engine(db_uri)
    metadata.create_all(engine)


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        PricePull,
        pull_table,
        properties={
            "pull_id": pull_table.c.pull_id,
            "kind": pull_table.c.kind,
            "status": pull_table.c.status,
            "version_number": pull_table.c.version_number,
        },
        primary_key=[pull_table.c.pull_id],
        version_id_col=pull_table.c.version_number,
    )
    event.listen(
        PricePull,
        "load",
        lambda obj, _: obj.init_transients(),
    )
