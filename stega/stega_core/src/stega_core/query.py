from dataclasses import dataclass

from stega_core.view import View


@dataclass(frozen=True, kw_only=True)
class Query[TView: View]:
    pass
