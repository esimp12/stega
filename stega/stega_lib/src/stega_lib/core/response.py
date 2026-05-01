from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from stega_lib.core.view import View


class QueryStatus(Enum):
    OK: str = "ok"
    FAILED: str = "failed"


class SubmissionStatus(Enum):
    ACCEPTED: str = "accepted"
    FAILED: str = "failed"


@dataclass(frozen=True, kw_only=True)
class Response(ABC):
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(frozen=True, kw_only=True)
class CommandResponse(Response):
    status: SubmissionStatus
    correlation_id: str


@dataclass(frozen=True, kw_only=True)
class QueryResponse[TView: View](Response):
    status: QueryStatus
    result: Optional[TView] = None
