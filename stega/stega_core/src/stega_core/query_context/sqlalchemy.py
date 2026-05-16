from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from stega_core.query_context.base import AbstractQueryContext

if TYPE_CHECKING:
    from stega_core.registry import ReaderRegistry


class SqlAlchemyQueryContext(AbstractQueryContext[AsyncSession]):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        reader_factory_registry: ReaderRegistry[AsyncSession],
    ) -> None:
        super().__init__(reader_factory_registry)
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def _begin(self) -> AsyncSession:
        self._session = self._session_factory()
        return self._session

    async def _close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None
