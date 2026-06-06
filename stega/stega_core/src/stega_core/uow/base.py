from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from stega_core.repository import AbstractRepository

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    from stega_core.message import Event
    from stega_core.registry import RepositoryRegistry


class AbstractUnitOfWork[SessionT](ABC):
    def __init__(self, repo_factory_registry: RepositoryRegistry[SessionT]) -> None:
        self._repo_factory_registry = repo_factory_registry
        self._repos: dict[type[AbstractRepository], AbstractRepository] = {}
        self._entered: bool = False

    def repo[RepoT: AbstractRepository](self, repo_type: type[RepoT]) -> RepoT:
        if not self._entered:
            err_msg = f"{type(self).__name__}.repo() called outside unit of work context"
            raise RuntimeError(err_msg)
        repo = self._repos[repo_type]
        return cast("RepoT", repo)

    def collect_new_events(self) -> Iterator[Event]:
        for repo in self._repos.values():
            for aggregate in repo.seen:
                while aggregate.events:
                    yield aggregate.events.pop(0)

    async def __aenter__(self) -> AbstractUnitOfWork[SessionT]:
        session = await self._begin()
        for repo_type in self._repo_factory_registry.repo_types:
            repo_factory = self._repo_factory_registry.get(repo_type)
            self._repos[repo_type] = repo_factory(session)
        self._entered = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            self._entered = False
            self._repos.clear()
            await self._close()

    @abstractmethod
    async def _begin(self) -> SessionT: ...

    @abstractmethod
    async def _close(self) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
