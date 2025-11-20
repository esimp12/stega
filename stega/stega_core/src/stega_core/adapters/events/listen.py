import contextlib
import functools
import typing as T

import pika

from stega_lib.events import Event, EventType
from stega_core.config import CoreConfig
from stega_core.services.messagebus import MessageBus


def listener_callback(
    channel,
    method,
    properties,
    body,
    bus: MessageBus,
) -> None:
    """Callback for handling incoming events.

    Args:
        bus (MessageBus): The message bus to handle incoming events for.

    """
    event = Event.from_message(
        topic=method.routing_key,
        body=body,
    )
    bus.handle(event)


def start_listening(
    config: CoreConfig,
    bus: MessageBus,
    listener_callback: T.Callable = listener_callback,
) -> None:
    """Start a blocking connection for the application event consumer.

    Args:
        config (CoreConfig): Configuration for the core service.  
        listener_callback (Callable): A Callable callback for handling
            incoming events.

    """
    event_types = bus.get_event_types()
    exchange = config.STEGA_BROKER_EXCHANGE

    credentials = pika.PlainCredentials(
        config.STEGA_BROKER_USER,
        config.STEGA_BROKER_PASS,
    )
    parameters = pika.ConnectionParameters(
        host=config.STEGA_BROKER_HOST,
        port=config.STEGA_BROKER_PORT,
        credentials=credentials,
    )
    with pika.BlockingConnection(parameters) as conn:
        channel = conn.channel()
        channel.exchange_declare(
            exchange=exchange,
            exchange_type="direct",
        )
        result = channel.queue_declare(
            queue="",
            exclusive=True,
        )
        queue_name = result.method.queue
        for event_type in event_types:
            channel.queue_bind(
                exchange=exchange,
                queue=queue_name,
                routing_key=event_type.topic,
            )
        callback = functools.partial(listener_callback, bus=bus)
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True,
        )
        channel.start_consuming()

