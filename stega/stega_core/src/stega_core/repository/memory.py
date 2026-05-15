from __future__ import annotations

from typing import TYPE_CHECKING, cast

from stega_core.domain import Aggregate
from stega_core.repository.base import AbstractRepository

if TYPE_CHECKING:
    from collections.abc import Iterable


class AbstractInMemoryRepository[AggregateT: Aggregate](AbstractRepository[AggregateT]):
    def __init__(self) -> None:
        super().__init__()
        self._store = dict[object, AggregateT] = {}

    async def _add(self, aggregate: AggregateT) -> None:
        self._store[aggregate.id] = aggregate

    async def _get(self, aggregate_id: object) -> AggregateT | None:
        aggregate = self._store.get(aggregate_id)
        return cast("AggregateT | None", aggregate)

    async def _update(self, aggregate: AggregateT) -> None:
        self._store[aggregate.id] = aggregate

    async def _delete(self, aggregate: AggregateT) -> None:
        self._store.pop(aggregate.id, None)

    async def _list(self) -> Iterable[AggregateT]:
        aggregates = list(self._store.values())
        return cast("Iterable[AggregateT]", aggregates)
