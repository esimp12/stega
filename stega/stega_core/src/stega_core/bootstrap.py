from contextlib import asynccontextmanager

from stega_core.config import CoreConfig
from stega_core.ports.base import PortfolioServicePort
from stega_core.ports.http import HttpRestPortfolioServicePort
from stega_core.services.handlers import (
    COMMAND_HANDLERS,
    QUERY_HANDLERS,
    EVENT_HANDLERS,
    STREAMED_EVENTS,
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
from stega_lib.streams.base import StreamBroker, make_stream_broadcaster
from stega_lib.streams.memory import InMemoryStreamBroker


def build_container(config: CoreConfig) -> DependencyContainer:
    # SSE stream broker for client event streaming updates
    broker = InMemoryStreamBroker()

    # create service ports
    portfolio_service = HttpRestPortfolioServicePort()

    return DependencyContainer([
        Dependency(
            type=StreamBroker,
            scope=Scope.SINGLETON,
            provider=lambda: broker,
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
        query_registry=build_query_registry(container),
        event_registry=build_event_registry(container),
        container=container,
    )


@asynccontextmanager
async def service_lifespan(config: CoreConfig):
    container = build_container(config)
    bus = build_bus(config, container)
    broker = container.resolve_singleton(StreamBroker)

    await broker.start()
    await bus.start()
    try:
        yield bus
    finally:
        await bus.stop()
        await broker.stop()
