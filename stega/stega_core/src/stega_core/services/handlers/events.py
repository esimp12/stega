import multiprocessing

from stega_lib.events import Event


def enqueue_streamed_event(event: Event, ipc_queue: multiprocessing.Queue) -> None:
    """
    """
    ipc_queue.put(event.to_message())
