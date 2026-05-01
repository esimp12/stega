from abc import ABC

from stega_lib.core.view import View


@dataclass(frozen=True, kw_only=True)
class Query[TView: View](ABC):
    pass
