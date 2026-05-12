from __future__ import annotations

from stega_core.repository import AbstractRepository, RepositoryFactory
from stega_core.registry.base import Registry


class RepositoryRegistry[SessionT](Registry[type[AbstractRepository], RepositoryFactory[SessionT]]):
    @property
    def repo_types(self) -> set[type[AbstractRepository]]:
        return self.keys
