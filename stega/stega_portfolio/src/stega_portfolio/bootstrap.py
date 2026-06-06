import functools
import logging
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from stega_core import (
    InMemoryBroker,
    RabbitMqBroker,
    RabbitMqConnectionParameters,
    ReaderRuntime,
    RepositoryRuntime,
    Service,
    ServiceBrokerRuntime,
    ServiceBuilder,
    SqlAlchemyQueryContext,
    SqlAlchemyUnitOfWork,
)

from stega_portfolio.config import PortfolioConfig
from stega_portfolio.ports.reader.base import PortfolioReader
from stega_portfolio.ports.reader.sqlalchemy import SqlAlchemyPortfolioReader
from stega_portfolio.ports.repository.base import PortfolioRepository
from stega_portfolio.ports.repository.sqlalchemy import SqlAlchemyPortfolioRepository
from stega_portfolio.services.handlers import (
    COMMAND_HANDLERS,
    EVENT_HANDLERS,
    QUERY_HANDLERS,
    SERVICE_EVENTS,
)


def get_db_uri(
    config: PortfolioConfig,
    *,
    is_async: bool = True,
) -> str:
    if bool(config.REPOSITORY_RUNTIME & RepositoryRuntime.SQLITE):
        path = Path.expanduser(Path(config.DATA_DIR))
        name = config.REPOSITORY_DBNAME
        if not Path.exists(path):
            Path.mkdir(path)
        path = Path(path) / f"{name}.db"
        dialect = "+aiosqlite" if is_async else ""
        return f"sqlite{dialect}:///{path}"
    if bool(config.REPOSITORY_RUNTIME & RepositoryRuntime.POSTGRES):
        user = config.REPOSITORY_DBUSER
        password = quote_plus(config.REPOSITORY_DBPASS)
        host = config.REPOSITORY_DBHOST
        port = config.REPOSITORY_DBPORT
        name = config.REPOSITORY_DBNAME
        dialect = "+asyncpg" if is_async else ""
        return f"postgresql{dialect}://{user}:{password}@{host}:{port}/{name}"
    return ""


def build_sqlalchemy_session_factory(db_uri: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(db_uri)
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


def build_sqlite_session_factory(config: PortfolioConfig) -> async_sessionmaker[AsyncSession]:
    db_uri = get_db_uri(config)
    return build_sqlalchemy_session_factory(db_uri)


def build_postgres_session_factory(config: PortfolioConfig) -> async_sessionmaker[AsyncSession]:
    db_uri = get_db_uri(config)
    return build_sqlalchemy_session_factory(db_uri)


def build_in_memory_session_factory(_: PortfolioConfig) -> None:
    return None


def build_rabbitmq_service_broker(config: PortfolioConfig) -> RabbitMqBroker:
    connection_params = RabbitMqConnectionParameters(
        host=config.SERVICE_BROKER_HOST,
        port=config.SERVICE_BROKER_PORT,
        username=config.SERVICE_BROKER_USER,
        password=config.SERVICE_BROKER_PASS,
    )
    return RabbitMqBroker(
        connection_params=connection_params,
        exchange_name=config.SERVICE_BROKER_EXCHANGE_NAME,
    )


def build_in_memory_service_broker(_: PortfolioConfig) -> InMemoryBroker:
    return InMemoryBroker()


def build_service(config: PortfolioConfig) -> Service:
    sqlite_session_factory = functools.partial(build_sqlite_session_factory, config)
    postgres_session_factory = functools.partial(build_postgres_session_factory, config)

    builder = ServiceBuilder(config)
    # set runtimes
    builder = (
        builder.with_repository_runtime("REPOSITORY_RUNTIME")
        .with_reader_runtime("READER_RUNTIME")
        .with_service_broker_runtime("SERVICE_BROKER_RUNTIME")
    )

    # create repo constructs
    uow_session_factories = {
        RepositoryRuntime.POSTGRES: postgres_session_factory,
        RepositoryRuntime.SQLITE: sqlite_session_factory,
    }
    uow_classes = {
        RepositoryRuntime.POSTGRES: SqlAlchemyUnitOfWork,
        RepositoryRuntime.SQLITE: SqlAlchemyUnitOfWork,
    }
    portfolio_repositories = {
        RepositoryRuntime.POSTGRES: SqlAlchemyPortfolioRepository,
        RepositoryRuntime.SQLITE: SqlAlchemyPortfolioRepository,
    }
    builder = (
        builder.with_unit_of_work_sessions(uow_session_factories)
        .with_unit_of_work(uow_classes)
        .with_repository(PortfolioRepository, portfolio_repositories)
    )

    # create reader constructs
    qctx_session_factories = {
        ReaderRuntime.POSTGRES: postgres_session_factory,
        ReaderRuntime.SQLITE: sqlite_session_factory,
    }
    qctx_classes = {
        ReaderRuntime.POSTGRES: SqlAlchemyQueryContext,
        ReaderRuntime.SQLITE: SqlAlchemyQueryContext,
    }
    portfolio_readers = {
        ReaderRuntime.POSTGRES: SqlAlchemyPortfolioReader,
        ReaderRuntime.SQLITE: SqlAlchemyPortfolioReader,
    }
    builder = (
        builder.with_query_context_sessions(qctx_session_factories)
        .with_query_context(qctx_classes)
        .with_reader(PortfolioReader, portfolio_readers)
    )

    # create service broker
    service_broker_factories = {
        ServiceBrokerRuntime.RABBITMQ: build_rabbitmq_service_broker,
        ServiceBrokerRuntime.MEMORY: build_in_memory_service_broker,
    }
    builder = builder.with_service_broker(service_broker_factories)

    # create handlers
    builder = (
        builder.with_command_handlers(COMMAND_HANDLERS)
        .with_query_handlers(QUERY_HANDLERS)
        .with_event_handlers(EVENT_HANDLERS)
        .with_service_events(SERVICE_EVENTS)
    )

    return builder.build(logging.getLogger(__name__))
