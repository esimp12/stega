from __future__ import annotations

from stega_core.domain.repo.base import AbstractRepository, RepoClass
from stega_core.registry.base import Registry


class RepoClassRegistry[SessionT](Registry[type[AbstractRepository], RepoClass[SessionT]]):
    @property
    def repo_types(self) -> set[type[AbstractRepository]]:
        return self.keys
