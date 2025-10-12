"""A messaging layer responsible for ingesting, routing, and resolving messages."""

import typing as T

from stega_lib.events import Event, EventType

from stega_core.config import create_config, create_logger
from stega_core.domain.errors import CoreAppError

Message = Event


class MessageBus:
    """Maps domain events to service handlers.

    Attributes:
        event_handlers: A mapping of Event types to their respective service
            handlers.
        queue: A list of Message instances to distribute to handlers.

    """

    def __init__(
        self,
        event_handlers: dict[EventType, list[T.Callable[[Event], None]]],
    ) -> None:
        """Initialize the MessageBus."""
        self.event_handlers = event_handlers
        self.queue = []
        self.config = create_config()
        self.logger = create_logger(self.config)

    def get_event_types(self) -> list[EventType]:
        """Get the list of event types supported for handling by the message bus.

        Returns:
            A list of EventTypes.

        """
        return list(self.event_handlers.keys())

    def handle(self, message: Message) -> None:
        """Process a Message by routing it to the appropriate service handler.

        Args:
            message: A Message instance to submit to a service handler.

        Raises:
            A TypeError if message is not an Event.

        """
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, Event):
                self.handle_event(message)
            else:
                err_msg = f"Message {message} is not a Message"
                raise TypeError(err_msg)

    def handle_event(self, event: Event) -> None:
        """Process an Event by routing it to the appropriate service handler.

        Args:
            event: An Event instance to submit to a service handler.

        """
        event_type = type(event)
        for handler in self.event_handlers[event_type]:
            try:
                handler(event)
            except CoreAppError:
                self.logger.warning("Application error occurred while handling event %s", event_type)
                continue
            except Exception:
                self.logger.exception("Failed to handle event %s", event_type)
                continue
