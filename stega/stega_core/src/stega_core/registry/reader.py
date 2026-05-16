from __future__ import annotations

from stega_core.reader import AbstractReader, ReaderFactory
from stega_core.registry.base import Registry


class ReaderRegistry[SessionT](Registry[type[AbstractReader], ReaderFactory[SessionT]]):
    @property
    def reader_types(self) -> set[type[AbstractReader]]:
        return self.keys
