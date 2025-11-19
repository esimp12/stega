import contextlib
import typing as T

import pika

from stega_portfolio.config import PortfolioConfig, create_config
from stega_lib.events import Event


@contextlib.contextmanager
def acquire_events_channel(
    exchange_name: str,
    exchange_type: str = "direct",
) -> T.Generator:
    """Setup a channel connection to an external events broker for publishing.

    Args:
        exchange_name: A str of the name of the external exchange to connect to.
        exchange_type: A str of the type of exchange to declare for use.

    Yields:
        A channel to publish events to.

    """
    conn = pika.BlockingConnection()
    channel = conn.channel()
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type="direct",
    )
    yield channel
    conn.close()


def publish_event(event: Event) -> None:
    """Publish an event to the external event broker.

    Args:
        event: An Event to publish.

    """
    config = create_config()
    exchange_name = config.STEGA_BROKER_EXCHANGE
    with acquire_events_channel(
        exchnage_name=exchange_name,
        exchange_type="direct",
    ) as channel:
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=event.topic,
            body=event.to_message(),
        )
