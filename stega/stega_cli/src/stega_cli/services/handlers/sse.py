import json
import queue
import threading
import typing as T

from stega_lib import http


def submit_and_wait_for_event(
    base_url: str, topic: str, matches: T.Callable[[dict[str, T.Any]], bool], request_callback: T.Callable[[], None]
) -> dict[str, T.Any]:
    """Submits a request and waits for an expected target message.

    This will first start a background daemon thread that listens for a
    target message for a given SSE topic. A request is submitted that is
    expected to produce the target message on that same topic. Then this will
    wait for the background thread to find the target message, send the result
    back to the calling thread on a queue, and finally return this result
    to the initial caller.

    Args:
        base_url: A str of the base url of the SSE endpoint.
        topic: A str of the SSE topic to listen to.
        matches: A Callable that takes a SSE message and returns a bool
            indicating whether or not the given message matches the expected
            target message.
        request_callback: A Callable that submits a request. This should
            ultimately produce a streamed message that can be found on the
            given SSE topic. It takes no parameters and does not return anything.

    Returns:
        A dict of the submitted request's corresponding streamed target message.

    """
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
    """Listen for a specific message for the given SSE topic.

    Args:
        base_url: A str of the base url of the SSE endpoint.
        topic: A str of the SSE topic to listen to.
        ready_event: A threading.Event instance to indicate when the client
            has established the initial SSE stream connection.
        result_queue: A Queue instance to send the target message result to.
        matches: A Callable that takes a SSE message and returns a bool
            indicating whether or not the given message matches the expected
            target message.

    """
    topic_url = f"events/{topic}"
    with http.acquire_session(base_url, timeout=False) as session, session.stream("GET", topic_url) as resp:
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
