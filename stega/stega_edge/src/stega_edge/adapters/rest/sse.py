import json
from dataclasses import dataclass

from quart import Blueprint, make_response

from stega_edge.adapters.rest.utils import get_bus, get_client_broker


api = Blueprint("edge_events_api", __name__)


@api.route("/events/<string:topic>")
async def stream_events(topic: str):
    bus = get_bus()
    if topic not in bus.subscribed_topics:
        return {
            "ok": False,
            "msg": f"No topic found for '{topic}'!",
        }, 400

    client_broker = get_client_broker()

    async def send_events():
        async for envelope in client_broker.subscribe(topic):
            event = ServerSentEvent(
                data=json.dumps(envelope.payload),
                event=envelope.topic,
            )
            yield event.encode()

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Transfer-Encoding": "chunked",
    }
    response = await make_response(send_events(), headers)
    response.timeout = None
    return response


@dataclass
class ServerSentEvent:
    data: str
    event: str | None = None
    sse_id: int | None = None
    retry: int | None = None

    def encode(self) -> bytes:
        message = f"data: {self.data}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        if self.sse_id is not None:
            message = f"{message}\nid: {self.sse_id}"
        if self.retry is not None:
            message = f"{message}\nretry: {self.retry}"
        messag = f"{message}\n\n"
        return message.encode("utf-8")
