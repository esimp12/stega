from typing import Callable, Optional

from stega_lib.core.response import Response
from stega_lib.di import HandlerBinding, Action


class Registry[TAction: Action, TResponse: Response | None]:

    def __init__(self) -> None:
        self._handlers: dict[type[TAction], HandlerBinding[TAction, TResponse]] = {}
        self._frozen = False

    def register[T: TAction](self, action_type: type[T], handler: HandlerBinding[T, TResponse]) -> None:
        if self._frozen:
            err_msg = "Registry is frozen; cannot register new handlers"
            raise RuntimeError(err_msg)
        if action_type in self._handlers:
            err_msg = f"Handler already registered for {action_type.__name__}"
            raise ValueError(err_msg)
        self._handlers[action_type] = handler

    def get(self, action_type: type[TAction]) -> Optional[HandlerBinding[TAction, TResponse]]:
        return self._handlers.get(action_type)

    def __contains__(self, action_type: type[TAction]) -> bool:
        return action_type in self._handlers

    def freeze(self) -> None:
        self._frozen = True


class FanOutRegistry[TAction: Action, TResponse: Response | None]:

    def __init__(self) -> None:
        self._handlers: dict[type[TAction], list[HandlerBinding[TAction, TResponse]] = {}
        self._frozen = False

    def register[T: TAction](self, action_type: type[T], handler: HandlerBinding[T, TReponse]) -> None:
        if self._frozen:
            err_msg = "Registry is frozen; cannot register new handlers"
            raise RuntimeError(err_msg)
        self._handlers.setdefault(action_type, []).append(handler)

    def get(self, action_type: type[TAction]) -> list[HandlerBinding[TAction, TResponse]]:
        return self._handlers.get(action_type, [])

    def __contains__(self, action_type: type[TAction]) -> bool:
        return action_type in self._handlers

    def freeze(self) -> None:
        self._frozen = True
