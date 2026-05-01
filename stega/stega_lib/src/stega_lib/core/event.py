from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, fields
from enum import Enum
from typing import ClassVar


class classproperty:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
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

    def __init_subclass__(cls, **kwargs):
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
                err_msg = f"Topic '{cls.topic}' already registered to {existing.__name__}; cannot re-register to {cls.__name__}"
                raise ValueError(err_msg)
        Event._registry[cls.topic] = cls

    @classmethod
    def for_topic(cls, topic: str) -> type[Event]:
        try:
            return cls._registry[topic]
        except KeyError:
            err_msg = f"No event registered for topic '{topic}'"
            raise KeyError(err_msg)

    def serialize(self) -> dict:
        return {
            "topic": self.topic,
            "correlation_id": self.correlation_id,
            "payload": self._serialize_payload(), 
        }

    def _serialize_payload(self) -> dict:
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name not in ("correlation_id",)
        }

    @classmethod
    def deserialize(cls, data: dict) -> Event:
        topic = data["topic"]
        correlation_id = data["correlation_id"]
        event_cls = cls.for_topic(topic)
        return event_cls._deserialize_payload(correlation_id, payload)

    @classmethod
    def _deserialize_payload(cls, correlation_id: str, payload: dict) -> Event:
        return cls(correlation_id=correlation_id, **payload)

    @classproperty
    def topics(cls) -> list[str]:
        return list(cls._registry.keys())

    @classproperty
    def event_types(cls) -> list[type[Event]]:
        return list(cls._registery.values())


@dataclass(frozen=True, kw_only=True)
class PortfolioCreated(Event):
    topic: ClassVar[str] = "portfolio_created"
    correlation_id: str
    portfolio_id: str
    name: str
    assets: list[dict[str, str | float]]


@dataclass(frozen=True, kw_only=True)
class PortfolioDeleted(Event):
    topic: ClassVar[str] = "portfolio_deleted"
    correlation_id: str
    portfolio_id: str


@dataclass(frozen=True, kw_only=True)
class PortfolioUpdated(Event):
    topic: ClassVar[str] = "portfolio_updated"
    correlation_id: str
    portfolio_id: str
