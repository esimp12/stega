import json
from collections.abc import Iterator
from queue import Empty, Queue

from flask import Blueprint
from stega_lib.events import ALL_EVENT_TOPICS

from stega_core.adapters.rest.utils import ResponseType, get_client_streams
from stega_core.config import create_config, create_logger

api = Blueprint("core_events_api", __name__)


@api.route("/events/<string:topic>")
def stream_events(topic: str) -> ResponseType | tuple[Iterator[str], int, dict[str, str]]:
    """Stream server side events processed from events consumer."""
    if topic not in ALL_EVENT_TOPICS:
        return {
            "ok": False,
            "msg": f"No topic found for '{topic}'!",
        }, 400

    headers = {"Content-Type": "text/event-stream"}
    streamed = stream_topic(topic)
    return streamed, 200, headers


def stream_topic(topic: str) -> Iterator[str]:
    """Stream SSE messages to all clients subscribed to the given topic.

    Args:
        topic: A str of the topic the SSE messages are associated with.

    Yields:
        A str of the SSE message sent to the client for the given topic.

    """
    client_queue = Queue()
    streams = get_client_streams()
    streams.add_topic_queue(topic, client_queue)

    config = create_config()
    logger = create_logger(config)
    try:
        while True:
            try:
                msg = client_queue.get(timeout=0.5)
                data = json.loads(msg)
            except Empty:
                yield '{"type": "heartbeat"}\n'
                continue
            logger.info("SSE topic '%s' got message => '%s'", topic, msg)
            data["type"] = "message"
            yield f"{json.dumps(data)}\n"
    finally:
        logger.info("SSE topic '%s' cleanup", topic)
        streams.remove_topic_queue(topic, client_queue)
