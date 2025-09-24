import contextlib
import typing as T

import pika

from stega_lib.events import Event

EventType = type[Event]


def listener_callback(
    channel,
    method,
    properties,
    body,
) -> None:
    event = Event.from_message(method.routing_key, body)
    dispatch(event)


def start_listening(
    event_types: list[EventType],
    exchange: str = "events",
    listener_callback: T.Callable,
) -> None:
    """
    """
    conn = pika.BlockingConnection()
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
    for event_type in events_types:
        channel.queue_bind(
            exchange=exchange,
            queue=queue_name,
            routing_key=event_type.routing_key,
        )
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=listener_callback,
        auto_ack=True,
    )
    channel.start_consuming()

