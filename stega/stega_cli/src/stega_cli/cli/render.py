from __future__ import annotations

import json
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from stega_core import ServiceResult


def render(result: ServiceResult) -> None:
    if result.result is None:
        click.echo(result.msg)
        return
    if isinstance(result.result, dict) and "correlation_id" in result.result:
        click.echo(f"{result.msg} (correlation_id: {result.result['correlation_id']})")
        return
    click.echo(json.dumps(result.result, indent=2, default=str))
