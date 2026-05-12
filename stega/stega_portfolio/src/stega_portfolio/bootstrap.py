from contextlib import asynccontextmanager

from stega_portfolio.config import CoreConfig
from stega_portfolio.services.handlers import (
    COMMAND_HANDLERS,
    QUERY_HANDLERS,
    EVENT_HANDLERS,
    PUBLISHED_EVENTS,
)

from stega_lib import (
    Command,
    CommandRegistry,
    Event,
    EventRegistry,
    Dependency,
    DependencyContainer,
    MessageBus,
    Scope,
    AbstractUnitOfWork,
    SqlAlchemyUnitOfWork,
    RepoClassRegistry,
)
from stega_lib.transport.base import MessageTransport, make_publishing_handler
from stega_lib.transport.rabbitmq import RabbitMqTransport, RabbitMqConnectionParameters



def build_command_registry(container: DependencyContainer) -> CommandRegistry:
    registry = CommandRegistry()
    for handler in COMMAND_HANDLERS:
        binding = bind_handler(handler, container, Command)
        registry.register(binding.action_type, binding)
    registry.freeze()
    return registry


def build_query_registry(container: DependencyContainer) -> QueryRegistry:
    registry = QueryRegistry()
    for handler in QUERY_HANDLERS:
        binding = bind_handler(handler, container, Query)
        registry.register(binding.action_type, binding)
    registry.freeze()
    return registry


def build_event_registry(container: DependencyContainer) -> EventRegsitry:
    registry = EventRegistry()
    
    # publishable events
    for event_type in PUBLISHED_EVENTS:
        handler = make_publishing_handler(event_type)
        binding = bind_handler(handler, container, Event)
        registry.register(binding.action_type, binding)

    # downstream work handlers responding to event effects 
    for handler in EVENT_HANDLERS:
        binding = bind_handler(handler, container, Event)
        registry.register(binding.action_type, binding)

    registry.freeze()
    return registry


def build_repo_registry() -> RepoClassRegistry[AsyncSession]:
    registry = RepoClassRegistry[AsyncSession]()
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


def build_transport(config: PortfolioConfig) -> RabbitMqTransport:
    transport = RabbitMqTransport(
        connection_parameters=RabbitMqConnectionParameters(
            host=config.STEGA_BROKER_HOST,
            port=config.STEGA_BROKER_PORT,
            username=config.STEGA_BROKER_PASSWORD,
            password=config.STEGA_BROKER_USERNAME,
        ),
        exchange_name=config.STEGA_BROKER_EXCHANGE_NAME,
    )
    return transport


def build_container(config: PortfolioConfig) -> DependencyContainer:
    session_factory = build_session_factory(config)
    repo_registry = build_repo_registry()
    transport = build_transport(config)
    
    return DependencyContainer([
        Dependency(
            type=MessageTransport,
            scope=Scope.SINGLETON,
            provider=lambda: transport,
        ),
        Dependency(
            type=AbstractUnitOfWork,
            scope=Scope.DISPATCH,
            provider=lambda: SqlAlchemyUnitOfWork(session_factory, repo_registry),
        ),
    ])


def build_bus(config: PortfolioConfig, container: DependencyContainer) -> MessageBus:
    return MessageBus(
        command_registry=build_command_registry(container),
        query_registry=build_query_registry(container),
        event_registry=build_event_registry(container),
        container=container,
    )


@asynccontextmanager
async def service_lifespan(config: PortfolioConfig):
    container = build_container(config)
    bus = build_bus(config, container)
    transport = container.resolve_singleton(MessageTransport)

    # start messaging constructs
    await transport.start()
    await bus.start()

    # manage service lifespan
    try:
        yield bus
    finally:
        await bus.stop()
        await transport.stop()
