import time
from queue import Queue, Empty
import typing as T

from flask import Blueprint, stream_with_context

from stega_core.config import create_config, create_logger
from stega_core.adapters.rest.utils import ResponseType, get_client_streams
from stega_core.services.handlers.streams import ClientStreams 
from stega_lib.events import ALL_EVENT_TOPICS


api = Blueprint("core_events_api", __name__)


@api.route("/events/<string:topic>")
def stream_events(topic: str) -> T.Generator[ResponseType, None, None]:
    """Stream server side events processed from events consumer."""
    if topic not in ALL_EVENT_TOPICS:
        return {
            "ok": False,
            "msg": f"No topic found for '{topic}'!"
        }, 400

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
) -> T.Generator[str, None, None]:
    config = create_config()
    logger = create_logger(config)
    try:
        while True:
            try:
                msg = client_queue.get(timeout=0.5)
            except Empty:
                yield "heartbeat\n"
                continue
            logger.info("SSE topic '%s' got message => '%s'", topic, msg) 
            yield msg
    finally:
        logger.info("SSE topic '%s' cleanup", topic)
        streams.remove_topic_queue(topic, client_queue)

