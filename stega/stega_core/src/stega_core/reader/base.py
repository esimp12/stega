from __future__ import annotations

from typing import Protocol


class ReaderFactory[SessionT](Protocol):
    def __call__(self, session: SessionT, /) -> AbstractReader: ...


class AbstractReader:
    pass
