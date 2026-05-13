from dataclasses import dataclass

from stega_core import Command


@dataclass(frozen=True, kw_only=True)
class CreatePortfolio(Command):
    name: str
    assets: dict[str, float]


@dataclass(frozen=True, kw_only=True)
class DeletePortfolio(Command):
    portfolio_id: str


@dataclass(frozen=True, kw_only=True)
class UpdatePortfolio(Command):
    portfolio_id: str
    name: str
    assets: dict[str, float]
