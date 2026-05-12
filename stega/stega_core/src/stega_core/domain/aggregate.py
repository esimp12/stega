from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stega_core.event import Event


class Aggregate:
    def __init__(self, aggregate_id: str, version_number: int = 0) -> None:
        self.aggregate_id: str = aggregate_id
        self.version_number: int = version_number
        self.events: list[Event] = []
