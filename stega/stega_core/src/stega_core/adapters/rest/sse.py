import time
from queue import Queue
import typing as T

from flask import Blueprint, stream_with_context

from stega_core.adapters.rest.utils import ResponseType, get_client_streams


api = Blueprint("core_events_api", __name__)


@api.route("/events/<topic:string>")
def stream_events(topic: str) -> T.Generator[ResponseType, None, None]:
    """Stream server side events processed from events consumer."""
    new_queue = Queue()
    streams = get_client_streams()
    streams.add_topic_queue(topic, new_queue)

    headers = {
        "Content-Type": "text/event-stream",
    }
    streamed = stream_topic(
        topic=topic,
        client_queue=new_queue,
        streams=streams,
    )
    return streamed, 200, headers
    

def stream_topic(
    topic: str,
    client_queue: Queue,
    streams: ClientStreams,
) -> str:
    try:
        while True:
            yield client_queue.get()
    finally:
        streams.remove_topic_queue(topic, client_queue)

