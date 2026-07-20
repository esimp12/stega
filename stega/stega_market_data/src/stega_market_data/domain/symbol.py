from typing import ClassVar

from stega_core import Aggregate


class Symbol(Aggregate):
    __id_attr__: ClassVar[str] = "ticker"

    def __init__(
        self,
        ticker: str,
        name: str,
        *,
        active: bool = True,
        version_number: int = 0,
    ) -> None:
        super().__init__(version_number)
        self.ticker = ticker
        self.name = name
        self.active = active
