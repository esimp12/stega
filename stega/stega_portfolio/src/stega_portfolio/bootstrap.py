from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from stega_core import (
    AbstractUnitOfWork,
    Command,
    CommandRegistry,
    Dependency,
    DependencyContainer,
    Event,
    EventRegistry,
    MessageBus,
    Query,
    QueryRegistry,
    RabbitMqBroker,
    RabbitMqConnectionParameters,
    RepositoryRegistry,
    Scope,
    ServiceBroker,
    SqlAlchemyUnitOfWork,
    bind_handler,
    make_service_publish_handler,
)

from stega_portfolio.config import PortfolioConfig
from stega_portfolio.ports.orm import start_mappers
from stega_portfolio.ports.repository.base import PortfolioRepository
from stega_portfolio.ports.repository.sqlalchemy import SqlAlchemyPortfolioRepository
from stega_portfolio.services.handlers import (
    COMMAND_HANDLERS,
    EVENT_HANDLERS,
    QUERY_HANDLERS,
    SERVICE_EVENTS,
)


def build_container(config: PortfolioConfig) -> DependencyContainer:
    # create external message broker
    service_broker = RabbitMqBroker(
        connection_parameters=RabbitMqConnectionParameters(
            host=config.STEGA_BROKER_HOST,
            port=config.STEGA_BROKER_PORT,
            username=config.STEGA_BROKER_PASSWORD,
            password=config.STEGA_BROKER_USERNAME,
        ),
        exchange_name=config.STEGA_BROKER_EXCHANGE_NAME,
    )

    # create session factory and repo registry for uow
    session_factory = build_session_factory(config)
    repo_registry = build_repo_registry()

    return DependencyContainer(
        [
            Dependency(
                type=ServiceBroker,
                scope=Scope.SINGLETON,
                provider=lambda: service_broker,
            ),
            Dependency(
                type=AbstractUnitOfWork,
                scope=Scope.DISPATCH,
                provider=lambda: SqlAlchemyUnitOfWork(session_factory, repo_registry),
            ),
        ]
    )


def build_command_registry() -> CommandRegistry:
    registry = CommandRegistry()
    for handler in COMMAND_HANDLERS:
        binding = bind_handler(handler, Command)
        registry.register(binding.action_type, binding)
    registry.freeze()
    return registry


def build_query_registry() -> QueryRegistry:
    registry = QueryRegistry()
    for handler in QUERY_HANDLERS:
        binding = bind_handler(handler, Query)
        registry.register(binding.action_type, binding)
    registry.freeze()
    return registry


def build_event_registry() -> EventRegistry:
    registry = EventRegistry()

    # service broker events
    for event_type in SERVICE_EVENTS:
        handler = make_service_publish_handler(event_type)
        binding = bind_handler(handler, Event)
        registry.register(binding.action_type, binding)

    # downstream work handlers responding to event effects
    for handler in EVENT_HANDLERS:
        binding = bind_handler(handler, Event)
        registry.register(binding.action_type, binding)

    registry.freeze()
    return registry


def build_repo_registry() -> RepositoryRegistry[AsyncSession]:
    registry = RepositoryRegistry[AsyncSession]()
    registry.register(
        PortfolioRepository,
        SqlAlchemyPortfolioRepository,
    )
    registry.freeze()
    return registry


def build_session_factory(config: PortfolioConfig) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(config.db_uri)
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


def build_bus(container: DependencyContainer) -> MessageBus:
    return MessageBus(
        command_registry=build_command_registry(),
        query_registry=build_query_registry(),
        event_registry=build_event_registry(),
        container=container,
    )


@dataclass
class ServiceLifespan:
    service_broker: ServiceBroker
    bus: MessageBus


@asynccontextmanager
async def service_lifespan(
    config: PortfolioConfig,
    *,
    start_orm: bool = False,
) -> AsyncIterator[ServiceLifespan]:
    # handle persistence mappings
    if start_orm:
        start_mappers()

    # construct messaging infrastructure
    container = build_container(config)
    bus = build_bus(container)
    service_broker = container.resolve_singleton(ServiceBroker)

    # start messaging constructs
    await service_broker.start()
    await bus.start()

    # manage service lifespan
    try:
        yield ServiceLifespan(
            service_broker=service_broker,
            bus=bus,
        )
    finally:
        await bus.stop()
        await service_broker.stop()
