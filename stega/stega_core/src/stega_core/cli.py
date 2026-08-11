from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from stega_core.message import Message


class ParamKind(StrEnum):
    ARGUMENT = "argument"
    OPTION = "option"


@dataclass(frozen=True, kw_only=True)
class CliParam:
    key: str
    kind: ParamKind = ParamKind.ARGUMENT
    help: str = ""
    flags: tuple[str, ...] = ()
    input_type: type = str
    required: bool = True
    parser: Callable[[Any], Any] | None = None
    factory: Callable[[], Any] | None = None

    @property
    def decls(self) -> tuple[str, ...]:
        if self.kind is ParamKind.ARGUMENT:
            return (self.key,)
        flags = self.flags or (f"--{self.key.replace('_', '-')}",)
        return (*flags, self.key)


@dataclass(frozen=True, kw_only=True)
class CliCommand:
    group: str
    name: str
    msg_type: type[Message]
    help: str = ""
    params: list[CliParam] = field(default_factory=list)
