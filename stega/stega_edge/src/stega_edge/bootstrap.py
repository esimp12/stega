import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass

from stega_core import (
    ClientBroker,
    Command,
    CommandRegistry,
    Dependency,
    DependencyContainer,
    Event,
    EventRegistry,
    InMemoryBroker,
    MessageBus,
    Query,
    QueryRegistry,
    RabbitMqBroker,
    RabbitMqConnectionParameters,
    Scope,
    ServiceBroker,
    bind_handler,
    make_client_publish_handler,
    make_service_publish_handler,
)

from stega_edge.config import EdgeConfig
from stega_edge.ports.base import PortfolioServicePort
from stega_edge.ports.http import HttpRestPortfolioServicePort
from stega_edge.services.handlers import (
    CLIENT_EVENTS,
    COMMAND_HANDLERS,
    EVENT_HANDLERS,
    QUERY_HANDLERS,
    SERVICE_EVENTS,
)


def build_container(config: EdgeConfig) -> DependencyContainer:
    # create internal and external message brokers
    service_broker = RabbitMqBroker(
        connection_parameters=RabbitMqConnectionParameters(
            host=config.STEGA_BROKER_HOST,
            port=config.STEGA_BROKER_PORT,
            username=config.STEGA_BROKER_PASSWORD,
            password=config.STEGA_BROKER_USERNAME,
        ),
        exchange_name=config.STEGA_BROKER_EXCHANGE_NAME,
    )
    client_broker = InMemoryBroker()

    # create service ports
    portfolio_service = HttpRestPortfolioServicePort()

    return DependencyContainer(
        [
            Dependency(
                type=ServiceBroker,
                scope=Scope.SINGLETON,
                provider=lambda: service_broker,
            ),
            Dependency(
                type=ClientBroker,
                scope=Scope.SINGLETON,
                provider=lambda: client_broker,
            ),
            Dependency(
                type=PortfolioServicePort,
                scope=Scope.SINGLETON,
                provider=lambda: portfolio_service,
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

    # service based broker events
    for event_type in SERVICE_EVENTS:
        handler = make_service_publish_handler(event_type)
        binding = bind_handler(handler, Event)
        registry.register(binding.action_type, binding)

    # client based broker events
    for event_type in CLIENT_EVENTS:
        handler = make_client_publish_handler(event_type)
        binding = bind_handler(handler, Event)
        registry.register(binding.action_type, binding)

    # downstream work handlers responding to event effects
    for handler in EVENT_HANDLERS:
        binding = bind_handler(handler, Event)
        registry.register(binding.action_type, binding)

    registry.freeze()
    return registry


def build_bus(container: DependencyContainer) -> MessageBus:
    return MessageBus(
        command_registry=build_command_registry(),
        query_registry=build_query_registry(),
        event_registry=build_event_registry(),
        container=container,
    )


async def run_service_broker_consumer(
    broker: ServiceBroker,
    topics: list[str],
    on_event: Callable[[Event], Awaitable[None]],
) -> None:
    async for envelope in broker.subscribe(topics):
        try:
            event = Event.deserialize(envelope.payload)
            await on_event(event)
        except Exception:
            pass


@dataclass
class ServiceLifespan:
    service_broker: ServiceBroker
    client_broker: ClientBroker
    bus: MessageBus


@asynccontextmanager
async def service_lifespan(config: EdgeConfig) -> AsyncIterator[ServiceLifespan]:
    # construct messaging infrastructure
    container = build_container(config)
    bus = build_bus(container)
    service_broker = container.resolve_singleton(ServiceBroker)
    client_broker = container.resolve_singleton(ClientBroker)

    # start messaging constructs
    await service_broker.start()
    await client_broker.start()
    await bus.start()

    # create background task for consuming external events
    consumer_task = asyncio.create_task(
        run_service_broker_consumer(
            broker=service_broker,
            topics=list(bus.subscribed_topics),
            on_event=bus.handle_event,
        ),
        name="service-broker-consumer",
    )

    # manage service lifespan
    try:
        yield ServiceLifespan(
            service_broker=service_broker,
            client_broker=client_broker,
            bus=bus,
        )
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        await bus.stop()
        await client_broker.stop()
        await service_broker.stop()
