import threading
from queue import Queue, Full
import typing as T


class ClientStreams:

    def __init__(self):
        self._streams = {}
        self._lock = threading.Lock()

    def add_topic_queue(self, topic: str, queue: Queue):
        with self._lock:
            self._streams.setdefault(topic, []).append(queue)
    
    def remove_topic_queue(self, topic: str, queue: Queue):
        with self._lock:
            self._streams[topic].remove(queue)
            if not self._streams[topic]:
                del self._streams[topic]

    def broadcast_topic(self, topic: str, payload: dict[str, T.Any]):
        with self._lock:
            queues = self._streams.get(topic, [])
        for q in queues:
            try:
                q.put_nowait(payload)
            except Full:
                pass

