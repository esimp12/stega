from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from stega_lib.domain.repo.base import AbstractRepository

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    from stega_lib.core.event import Event
    from stega_lib.registry.repo import RepoClassRegistry


class AbstractUnitOfWork[SessionT](ABC):
    def __init__(self, repo_class_registry: RepoClassRegistry[SessionT]) -> None:
        self._repo_class_registry = repo_class_registry
        self._repos: dict[type[AbstractRepository], AbstractRepository] = {}
        self._entered: bool = False

    def repo[RepoT: AbstractRepository](self, repo_type: type[RepoT]) -> RepoT:
        if not self._entered:
            err_msg = f"{type(self).__name__}.repo() called outside unit of work context"
            raise RuntimeError(err_msg)
        repo = self._repos[repo_type]
        return cast("repo_type", repo)

    def collect_new_events(self) -> Iterator[Event]:
        for repo in self._repos.values():
            for aggregate in repo.seen:
                while aggregate.events:
                    yield aggregate.events.pop(0)

    async def __aenter__(self) -> AbstractUnitOfWork[SessionT]:
        session = await self._begin()
        for repo_type in self._repo_class_registry.types():
            repo_class = self._repo_class_registry.get(repo_type)
            self._repos[repo_type] = repo_class(session)
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
