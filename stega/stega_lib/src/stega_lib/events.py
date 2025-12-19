"""Module for common event types used across the stega application."""

from __future__ import annotations

import abc
import json
import typing as T

from stega_lib.domain import Command


class Event(abc.ABC):
    """Base class for all events."""

    correlation_id: T.Optional[str] 
    topic: str = "events"

    def __post_init__(self) -> None:
        if self.correlation_id is None:
            self.correlation_id = Command.gen_id()

    @classmethod
    def from_message(cls, topic: str, body: str) -> Event:
        """Create an Event from its topic and incoming raw message.
        
        Args:
            topic (str): The event topic to source an event for.
            body (str): The raw event message to extract into event args.

        Returns:
            An Event to process.

        """
        if topic not in EVENTS_MAPPING:
            err_msg = f"'{topic}' is not a recognized event topic"
            raise ValueError(err_msg)

        event_type = EVENTS_MAPPING[topic]
        kwargs = json.loads(body)
        return event_type(**kwargs)

    @abc.abstractmethod
    def to_message(self) -> str:
        """Serialize an event so that it may be sent as a raw message.

        Returns:
            A serialized event as a str.

        """
        err_msg = "'to_message' not implemented"
        raise NotImplementedError(err_msg)


class PortfolioCreated(Event):
    """Event indicating that a portfolio has been created.

    Attributes:
        id: The unique identifier of the created portfolio.
    """

    topic: str = "portfolio_created"

    def __init__(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Initialize the PortfolioCreated event."""
        self.id = id

    def to_message(self) -> str:
        """See Event."""
        body = {
            "id": self.id,
        }
        if self.correlation_id is not None:
            body["correlation_id"] = self.correlation_id
        return json.dumps(body)


class PortfolioDeleted(Event):
    """Event indicating that a portfolio has been deleted.

    Attributes:
        id: The unique identifier of the deleted portfolio.
    """

    topic: str = "portfolio_deleted"

    def __init__(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Initialize the PortfolioDeleted event."""
        self.id = id

    def to_message(self) -> str:
        """See Event."""
        body = {
            "id": self.id,
        }
        if self.correlation_id is not None:
            body["correlation_id"] = self.correlation_id
        return json.dumps(body)


class PortfolioUpdated(Event):
    """Event indicating that a portfolio has been updated.

    Attributes:
        id: The unique identifier of the updated portfolio.
    """

    topic: str = "portfolio_updated"

    def __init__(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Initialize the PortfolioUpdated event."""
        self.id = id

    def to_message(self) -> str:
        """See Event."""
        body = {
            "id": self.id,
        }
        if self.correlation_id is not None:
            body["correlation_id"] = self.correlation_id
        return json.dumps(body)


EventType = type[Event]

EVENTS_MAPPING: dict[str, EventType] = {
    event_type.topic: event_type
    for event_type in [
        PortfolioCreated,
        PortfolioUpdated,
        PortfolioDeleted,
    ]
}

ALL_EVENT_TOPICS = list(EVENTS_MAPPING.keys())

