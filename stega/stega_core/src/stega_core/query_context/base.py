from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from stega_core.reader import AbstractReader

if TYPE_CHECKING:
    from types import TracebackType

    from stega_core.registry import ReaderRegistry


class AbstractQueryContext[SessionT](ABC):
    def __init__(self, reader_factory_registry: ReaderRegistry[SessionT]) -> None:
        self._reader_factory_registry = reader_factory_registry
        self._readers: dict[type[AbstractReader], AbstractReader] = {}
        self._entered: bool = False

    def reader[ReaderT: AbstractReader](self, reader_type: type[ReaderT]) -> ReaderT:
        if not self._entered:
            err_msg = f"{type(self).__name__}.reader() called outside query context"
            raise RuntimeError(err_msg)
        reader = self._readers[reader_type]
        return cast("ReaderT", reader)

    async def __aenter__(self) -> AbstractQueryContext[SessionT]:
        session = await self._begin()
        for reader_type in self._reader_factory_registry.reader_types():
            reader_factory = self._reader_factory_registry.get(reader_type)
            self._readers[reader_type] = reader_factory(session)
        self._entered = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._entered = False
        self._readers.clear()
        await self._close()

    @abstractmethod
    async def _begin(self) -> SessionT: ...

    @abstractmethod
    async def _close(self) -> None: ...
