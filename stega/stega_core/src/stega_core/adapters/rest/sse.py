import typing as T
import time

from flask import Blueprint, stream_with_context

from stega_core.adapters.rest.utils import ResponseType


api = Blueprint("core_events_api", __name__)


@api.route("/events/portfolio/created")
def stream_events() -> T.Generator[ResponseType, None, None]:
    """Stream server side events processed from events consumer."""
    global total
    total = 0

    @stream_with_context
    def generator():
        while True:
            time.sleep(1)
            global total
            total += 1
            yield f"Sleep for {total} seconds.\n"

    headers = {
        "Content-Type": "text/event-stream",
    }
    return generator(), 200, headers
    
