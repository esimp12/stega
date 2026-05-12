from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

from stega_lib.domain.aggregate import Aggregate

if TYPE_CHECKING:
    from collections.abc import Iterable


class RepoClass[SessionT](Protocol):
    def __call__(self, session: SessionT, /) -> AbstractRepository: ...


class AbstractRepository[AggregateT: Aggregate](ABC):
    def __init__(self) -> None:
        self.seen: set[Aggregate] = set()

    async def add(self, aggregate: AggregateT) -> None:
        await self._add(aggregate)
        self.seen.add(aggregate)

    async def get(self, aggregate_id: object) -> AggregateT | None:
        aggregate = await self._get(aggregate_id)
        if aggregate is not None:
            self.seen.add(aggregate)
        return aggregate

    async def update(self, aggregate: AggregateT) -> None:
        await self._update(aggregate)
        self.seen.add(aggregate)

    async def delete(self, aggregate: AggregateT) -> None:
        await self._delete(aggregate)
        self.seen.add(aggregate)

    async def list(self) -> Iterable[AggregateT]:
        aggregates = await self._list()
        for aggregate in aggregates:
            self.seen.add(aggregate)
        return aggregates

    @abstractmethod
    async def _add(self, aggregate: AggregateT) -> None: ...

    @abstractmethod
    async def _get(self, aggregate_id: object) -> AggregateT | None: ...

    @abstractmethod
    async def _update(self, aggregate: AggregateT) -> None: ...

    @abstractmethod
    async def _delete(self, aggregate: AggregateT) -> None: ...

    @abstractmethod
    async def _list(self) -> Iterable[AggregateT]: ...
