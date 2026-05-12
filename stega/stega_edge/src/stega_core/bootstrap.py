from contextlib import asynccontextmanager

from stega_core.config import CoreConfig
from stega_core.ports.base import PortfolioServicePort
from stega_core.ports.http import HttpRestPortfolioServicePort
from stega_core.services.handlers import (
    COMMAND_HANDLERS,
    QUERY_HANDLERS,
    EVENT_HANDLERS,
    STREAMED_EVENTS,
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
)
from stega_lib.streams.base import StreamBroker, make_broadcast_handler
from stega_lib.streams.memory import InMemoryStreamBroker
from stega_lib.transport.base import MessageTransport, make_publishing_handler
from stega_lib.transport.rabbitmq import RabbitMqTransport, RabbitMqConnectionParameters


def build_container(config: CoreConfig) -> DependencyContainer:
    # SSE stream broker for client event streaming updates
    broker = InMemoryStreamBroker()

    # Message transport for external events consumption
    transport = RabbitMqTransport(
        connection_parameters=RabbitMqConnectionParameters(
            host=config.STEGA_BROKER_HOST,
            port=config.STEGA_BROKER_PORT,
            username=config.STEGA_BROKER_PASSWORD,
            password=config.STEGA_BROKER_USERNAME,
        ),
        exchange_name=config.STEGA_BROKER_EXCHANGE_NAME,
    )

    # create service ports
    portfolio_service = HttpRestPortfolioServicePort()

    return DependencyContainer([
        Dependency(
            type=StreamBroker,
            scope=Scope.SINGLETON,
            provider=lambda: broker,
        )
        Dependency(
            type=MessageTransport,
            scope=Scope.SINGLETON,
            provider=lambda: transport,
        )
        Dependency(
            type=PortfolioServicePort,
            scope=Scope.SINGLETON,
            provider=lambda: portfolio_service, 
        ),
    ])


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

    # streamable events
    for event_type in STREAMED_EVENTS:
        handler = make_broadcast_handler(event_type)
        binding = bind_handler(handler, container, Event)
        registry.register(binding.action_type, binding)

    # downstream work handlers responding to event effects 
    for handler in EVENT_HANDLERS:
        binding = bind_handler(handler, container, Event)
        registry.register(binding.action_type, binding)

    registry.freeze()
    return registry


def build_bus(config: CoreConfig, container: DependencyContainer) -> MessageBus:
    return MessageBus(
        command_registry=build_command_registry(container),
        query_registry=build_query_registry(container), event_registry=build_event_registry(container),
        container=container,
    )


async def run_transport_consumer(
    transport: MessageTransport,
    topics: list[str],
    on_event: Callable[[Event], Awaitable[None]],
) -> None:
    async for transport_msg in transport.subscribe(topics):
        try:
            event = Event.deserialize(transport_msg.body)
            await on_event(event)
        except Exception:
            pass


@asynccontextmanager
async def service_lifespan(config: CoreConfig):
    # construct messaging infrastructure
    container = build_container(config)
    bus = build_bus(config, container)
    broker = container.resolve_singleton(StreamBroker)
    transport = container.resolve_singleton(MessageTransport)

    # start messaging constructs
    await transport.start()
    await broker.start()
    await bus.start()

    # create background task for consuming external events
    consumer_task = asyncio.create_task(
        run_transport_consumer(
            transport=transport,
            topics=list(bus.subscribed_topics),
            on_event=bus.handle_event,
        ),
        name="transport-consumer",
    )

    # manage service lifespan
    try:
        yield bus
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        await bus.stop()
        await broker.stop()
        await transport.stop()
