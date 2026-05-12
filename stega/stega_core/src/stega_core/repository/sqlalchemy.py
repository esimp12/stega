from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from sqlalchemy import select

from stega_core.domain import Aggregate
from stega_core.repository.base import AbstractRepository

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sqlalchemy.ext.asyncio import AsyncSession


class AbstractSqlAlchemyRepository[AggregateT: Aggregate](AbstractRepository[AggregateT]):
    model: ClassVar[type[Aggregate]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if getattr(cls, "__abstractmethods__", None):
            return

        if "model" not in cls.__dict__ and not hasattr(cls, "model"):
            err_msg = f"{cls.__name__} must define `model` as a class attribute"
            raise TypeError(err_msg)

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session

    async def _add(self, aggregate: AggregateT) -> None:
        self._session.add(aggregate)

    async def _get(self, aggregate_id: object) -> AggregateT | None:
        aggregate = await self._session.get(self.model, aggregate_id)
        return cast("AggregateT | None", aggregate)

    async def _update(self, _: AggregateT) -> None:
        return None

    async def _delete(self, aggregate: AggregateT) -> None:
        await self._session.delete(aggregate)

    async def _list(self) -> Iterable[AggregateT]:
        result = await self._session.execute(select(self.model))
        return cast("Iterable[AggregateT]", result.scalars().all())
