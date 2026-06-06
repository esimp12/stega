from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Command(ABC):
    pass
