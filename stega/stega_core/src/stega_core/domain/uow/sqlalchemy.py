from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from stega_core.domain.uow.base import AbstractUnitOfWork

if TYPE_CHECKING:
    from stega_core.registry.repo import RepoClassRegistry


class SqlAlchemyUnitOfWork(AbstractUnitOfWork[AsyncSession]):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repo_class_registry: RepoClassRegistry[AsyncSession],
    ) -> None:
        super().__init__(repo_class_registry)
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def _begin(self) -> AsyncSession:
        self._session = self._session_factory()
        return self._session

    async def _close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()
