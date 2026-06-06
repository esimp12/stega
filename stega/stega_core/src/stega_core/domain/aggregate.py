from typing import Any, ClassVar

from stega_core.message import Event, classproperty


class Aggregate:
    __id_attr__: ClassVar[str]

    def __init_subclass__(
        cls,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init_subclass__(**kwargs)
        if "__id_attr__" not in cls.__dict__:
            err_msg = f"{cls.__name__} must declare __id_attr__"
            raise TypeError(err_msg)

    def __init__(self, version_number: int = 0) -> None:
        self.version_number: int = version_number
        self.init_transients()

    def init_transients(self) -> None:
        self.events: list[Event] = []

    def record(self, event: Event) -> None:
        self.events.append(event)

    @classproperty
    def id_attr(self) -> str:
        return self.__id_attr__
