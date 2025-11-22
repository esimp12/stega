import os
import threading
from queue import Queue, Full
import typing as T

from stega_core.config import create_config, create_logger


class ClientStreams:

    def __init__(self):
        self._streams = {}
        self._lock = threading.Lock()
        self.config = create_config()
        self.logger = create_logger(self.config)
        self.logger.info(
            "ClientStreams created pid=%s self_id=%s",
            os.getpid(),
            hex(id(self)),
        )

    def add_topic_queue(self, topic: str, queue: Queue):
        with self._lock:
            self._streams.setdefault(topic, []).append(queue)
    
    def remove_topic_queue(self, topic: str, queue: Queue):
        with self._lock:
            self._streams[topic].remove(queue)
            if not self._streams[topic]:
                del self._streams[topic]

    def broadcast_topic(self, topic: str, payload: str):
        with self._lock:
            queues = self._streams.get(topic, [])
        for q in queues:
            try:
                self.logger.info("Putting payload '%s' in queue for topic '%s'", payload, topic)
                q.put_nowait(payload)
            except Full:
                continue

