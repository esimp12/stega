from dataclasses import dataclass
from enum import Enum

from stega_core.view import View


class QueryStatus(Enum):
    OK: str = "ok"
    FAILED: str = "failed"


class SubmissionStatus(Enum):
    ACCEPTED: str = "accepted"
    FAILED: str = "failed"


@dataclass(frozen=True, kw_only=True)
class Response:
    error: str | None = None

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
    result: TView | None = None
