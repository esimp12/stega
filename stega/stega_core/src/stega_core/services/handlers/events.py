from stega_lib.events import Event

from stega_core.services.handlers.streams import ClientStreams


def enqueue_streamed_event(event: Event, streams: ClientStreams) -> None:
    """Publish an event to all subscribed client streams.

    Args:
        event: An Event instance to publish.
        streams: A ClientStreams instance to broadcast the event to.

    """
    streams.broadcast_topic(event.topic, event.to_message())
