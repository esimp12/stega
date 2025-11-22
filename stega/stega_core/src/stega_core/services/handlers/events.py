import multiprocessing

from stega_lib.events import Event
from stega_core.services.handlers.streams import ClientStreams


def enqueue_streamed_event(event: Event, streams: ClientStreams) -> None:
    """
    """
    streams.broadcast_topic(event.topic, event.to_message())
