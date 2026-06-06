from contextvars import ContextVar
from typing import Any

_context: ContextVar[dict[str, Any] | None] = ContextVar("stega_context", default=None)


def current_context() -> dict[str, Any]:
    ctx = _context.get()
    if ctx is None:
        ctx = {}
        _context.set(ctx)
    return ctx


def set_context(frame: dict[str, Any]) -> None:
    _context.set(frame)
