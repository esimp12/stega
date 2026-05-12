from __future__ import annotations

from stega_lib.core.response import Response
from stega_lib.di import Action, HandlerBinding
from stega_lib.registry.base import FanOutRegistry, Registry


class ActionRegistry[TAction: Action, TResponse: Response | None](
    Registry[type[TAction], HandlerBinding[TAction, TResponse]]
):
    @property
    def action_types(self) -> set[type[TAction]]:
        return self.keys


class ActionFanOutRegistry[TAction: Action, TResponse: Response | None](
    FanOutRegistry[type[TAction], HandlerBinding[TAction, TResponse]]
):
    @property
    def action_types(self) -> set[type[TAction]]:
        return self.keys
