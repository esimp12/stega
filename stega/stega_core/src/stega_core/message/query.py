from dataclasses import dataclass

from stega_core.message.view import View


@dataclass(frozen=True, kw_only=True)
class Query[ViewT: View]:
    pass
