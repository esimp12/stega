import json
import queue
import threading
import typing as T

from stega_lib import http


def submit_and_wait_for_event(
    base_url: str,
    topic: str,
    matches: T.Callable[[dict[str, T.Any]], bool],
    request_callback: T.Callable[[], None],
) -> dict[str, T.Any]:
    ready_event = threading.Event()
    result_queue = queue.Queue(maxsize=1)
    # start listenting thread
    sse_thread = threading.Thread(
        target=sse_listener,
        kwargs={
            "base_url": base_url,
            "topic": topic,
            "ready_event": ready_event,
            "result_queue": result_queue,
            "matches": matches,
        },
        daemon=True,
    )
    sse_thread.start()
    # wait to establish stream connection
    ready_event.wait()
    # submit request
    request_callback()
    # get result
    return result_queue.get()


def sse_listener(
    base_url: str,
    topic: str,
    ready_event: threading.Event,
    result_queue: queue.Queue,
    matches: T.Callable[[dict[str, T.Any]], bool],
) -> None:
    topic_url = f"events/{topic}"
    with http.acquire_session(base_url, timeout=False) as session:
        with session.stream("GET", topic_url) as resp:
            # signal we have established stream connection
            ready_event.set()

            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                msg_type = data["type"]
                # skip heartbeats
                if msg_type == "heartbeat":
                    continue
                # check if we found the corresponding event
                if matches(data):
                    result_queue.put(data)
                    return

