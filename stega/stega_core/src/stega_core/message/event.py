from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, fields
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, overload

if TYPE_CHECKING:
    from collections.abc import Callable


class classproperty[T]:  # noqa: N801
    def __init__(self, fget: Callable[[type], T]) -> None:
        self.fget = fget

    @overload
    def __get__(self, _: None, owner: type) -> T: ...
    @overload
    def __get__(self, _: object, owner: type) -> T: ...
    def __get__(self, _: object | None, owner: type) -> T:
        return self.fget(owner)


class EventDispatch(Enum):
    SYNC: str = "sync"
    ASYNC: str = "async"


@dataclass(frozen=True, kw_only=True)
class Event(ABC):
    topic: ClassVar[str]
    dispatch: ClassVar[EventDispatch] = EventDispatch.ASYNC
    _registry: ClassVar[dict[str, type[Event]]] = {}

    correlation_id: str

    def __init_subclass__(
        cls,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init_subclass__(**kwargs)
        # abstract class, skip
        if getattr(cls, "__abstractmethods__", None):
            return
        # check that topic is set
        if not hasattr(cls, "topic") or not isinstance(cls.topic, str):
            err_msg = f"{cls.__name__} must define a class-level `topic: ClassVar[str]`"
            raise TypeError(err_msg)

        # register event type
        if cls.topic in Event._registry:
            existing = Event._registry[cls.topic]
            if existing is not cls:
                err_msg = (
                    f"Topic '{cls.topic}' already registered to {existing.__name__}; "
                    f"cannot re-register to {cls.__name__}"
                )
                raise ValueError(err_msg)
        Event._registry[cls.topic] = cls

    @classmethod
    def for_topic(cls, topic: str) -> type[Event]:
        try:
            return cls._registry[topic]
        except KeyError as err:
            err_msg = f"No event registered for topic '{topic}'"
            raise KeyError(err_msg) from err

    def serialize(self) -> dict:
        return {
            "topic": self.topic,
            "correlation_id": self.correlation_id,
            "payload": self._serialize_payload(),
        }

    def _serialize_payload(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name not in ("correlation_id",)}

    @classmethod
    def deserialize(cls, data: dict) -> Event:
        topic = data["topic"]
        correlation_id = data["correlation_id"]
        payload = data["payload"]
        event_cls = cls.for_topic(topic)
        return event_cls._deserialize_payload(correlation_id, payload)  # noqa: SLF001

    @classmethod
    def _deserialize_payload(cls, correlation_id: str, payload: dict) -> Event:
        return cls(correlation_id=correlation_id, **payload)

    @classproperty
    def topics(self) -> list[str]:
        return list(self._registry.keys())

    @classproperty
    def event_types(self) -> list[type[Event]]:
        return list(self._registry.values())
