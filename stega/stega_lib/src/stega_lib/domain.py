"""Common abstract interfaces for domain entities and aggregates."""

from dataclasses import dataclass, field
import typing as T

import uuid_utils as uuid


class Aggregate:
    """Abstract base class for all domain aggregates.

    Attributes:
        id: A str of the unique identity of an aggregate.
        version_number: An integer of the currently loaded version of this aggregate.
        events: A list of any domain events collected on this aggregate.

    """

    def __init__(
        self,
        id: str,  # noqa: A002
        version_number: int = 0,
    ) -> None:
        """Inits a domain aggregate."""
        self.id = id
        self.version_number = version_number
        self.events = []


class DomainEntity:
    """Abstract base class for all domain entities.

    Attributes:
        id: A str of the unique identity of a domain entity.

    """

    def __init__(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Inits a domain entity."""
        self.id = id


@dataclass
class Command:
    """Data message to perform specific service handler.

    Attributes:
        correlation_id: A str globally uniquely representing an event trace occuring
            throughout the system.
        action_id: A str locally uniquely representing an individual action occuring
            for the associated service.

    """

    correlation_id: T.Optional[str]
    action_id: T.Optional[str]

    def __post_init__(self) -> None:
        if self.correlation_id is None:
            self.correlation_id = self.gen_id()
        if action_id is None:
            self.action_id = self.gen_id()

    @staticmethod
    def gen_id() -> str:
        """Generates a unique identifier for entity creation commands.

        Returns:
            str: A unique UUIDv7 identifier.

        """
        return str(uuid.uuid7())


CommandType = type[Command]
