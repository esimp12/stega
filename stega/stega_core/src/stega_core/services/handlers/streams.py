import os
import threading
from queue import Full, Queue

from stega_core.config import create_config, create_logger


class ClientStreams:
    """Data mapping to support streaming topics for multiple clients.

    Maintains a mapping of topics to client queues where incoming messages are
    broadcasted to every queue associated with a topic. Supports multithreading,
    broadcasting, adding and removing new queues.

    """

    def __init__(self) -> None:
        self._streams = {}
        self._lock = threading.Lock()
        self.config = create_config()
        self.logger = create_logger(self.config)
        self.logger.info(
            "ClientStreams created pid=%s self_id=%s",
            os.getpid(),
            hex(id(self)),
        )

    def add_topic_queue(self, topic: str, queue: Queue) -> None:
        """Associate a new client queue with a given topic.

        Args:
            topic: A str of the topic the queue is associated with.
            queue: A Queue the client expects to receive incoming message on.

        """
        with self._lock:
            self._streams.setdefault(topic, []).append(queue)

    def remove_topic_queue(self, topic: str, queue: Queue) -> None:
        """Remove the existing client queue associated with the given topic.

        Args:
            topic: A str of the topic the queue is associated with.
            queue: A Queue the client expects to receive incoming message on.

        """
        with self._lock:
            self._streams[topic].remove(queue)
            if not self._streams[topic]:
                del self._streams[topic]

    def broadcast_topic(self, topic: str, payload: str) -> None:
        """Send a message to every client queue associated with the given topic.

        Args:
            topic: A str of the topic the message should be sent to.
            payload: A str of the message to send to each queue in the topic.

        """
        with self._lock:
            queues = self._streams.get(topic, [])
        for q in queues:
            try:
                self.logger.info("Putting payload '%s' in queue for topic '%s'", payload, topic)
                q.put_nowait(payload)
            except Full:
                continue
