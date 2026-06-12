import logging

from stega_contracts.portfolio import CONTRACT as PORTFOLIO_CONTRACT
from stega_core import (
    ClientBrokerRuntime,
    InMemoryBroker,
    RabbitMqBroker,
    RabbitMqConnectionParameters,
    Service,
    ServiceBrokerRuntime,
    ServiceBuilder,
)

from stega_edge.config import EdgeConfig
from stega_edge.services.handlers import (
    CLIENT_EVENTS,
    COMMAND_HANDLERS,
    EVENT_HANDLERS,
    QUERY_HANDLERS,
    SERVICE_EVENTS,
)


def build_rabbitmq_broker(config: EdgeConfig) -> RabbitMqBroker:
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


def build_in_memory_broker(_: EdgeConfig) -> InMemoryBroker:
    return InMemoryBroker()


def build_service(config: EdgeConfig) -> Service:
    builder = ServiceBuilder(config)

    # set runtimes
    builder = builder.with_service_broker_runtime("SERVICE_BROKER_RUNTIME").with_client_broker_runtime(
        "CLIENT_BROKER_RUNTIME"
    )

    # create service broker
    service_broker_factories = {
        ServiceBrokerRuntime.RABBITMQ: build_rabbitmq_broker,
        ServiceBrokerRuntime.MEMORY: build_in_memory_broker,
    }
    builder = builder.with_service_broker(service_broker_factories)

    # create client broker
    client_broker_factories = {
        ClientBrokerRuntime.MEMORY: build_in_memory_broker,
    }
    builder = builder.with_client_broker(client_broker_factories)

    # create service ports
    builder = builder.with_service_contracts(
        [
            PORTFOLIO_CONTRACT,
        ]
    )

    # create handlers
    builder = (
        builder.with_command_handlers(COMMAND_HANDLERS)
        .with_query_handlers(QUERY_HANDLERS)
        .with_event_handlers(EVENT_HANDLERS)
        .with_service_events(SERVICE_EVENTS)
        .with_client_events(CLIENT_EVENTS)
    )

    return builder.build(logging.getLogger(__name__))
