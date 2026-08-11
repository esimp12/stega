from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import click
from stega_core import AppError, CliCommand, CliParam, ParamKind, marshal

from stega_cli.bootstrap import build_client_port
from stega_cli.cli.render import render

if TYPE_CHECKING:
    from stega_core import Message, ServiceResult


def build_cli(
    root: click.Group,
    specs: list[CliCommand],
    groups: dict[str, str],
) -> click.Group:
    made: dict[str, click.Group] = {}
    for spec in specs:
        group = made.get(spec.group)
        if group is None:
            group = click.Group(name=spec.group, help=groups.get(spec.group, ""))
            made[spec.group] = group
            root.add_command(group)
        group.add_command(build_command(spec))
    return root


def build_command(spec: CliCommand) -> click.Command:
    return click.Command(
        name=spec.name,
        help=spec.help,
        callback=make_callback(spec),
        params=[build_param(p) for p in spec.params if p.factory is None],
    )


def build_param(param: CliParam) -> click.Parameter:
    if param.kind is ParamKind.ARGUMENT:
        return click.Argument(
            param.decls,
            type=param.input_type,
            required=param.required,
        )
    return click.Option(
        param.decls,
        type=param.input_type,
        required=param.required,
        default=None,
        help=param.help,
    )


def build_message(spec: CliCommand, values: dict[str, Any]) -> Message:
    payload: dict[str, Any] = {}
    for param in spec.params:
        if param.factory is not None:
            payload[param.key] = param.factory()
            continue
        raw = values.get(param.key)
        if raw is None:
            continue
        payload[param.key] = param.parser(raw) if param.parser is not None else raw
    return marshal(spec.msg_type, payload)


def make_callback(spec: CliCommand) -> Any:  # noqa: ANN401
    def callback(
        **values: Any,  # noqa: ANN401
    ) -> None:
        try:
            message = build_message(spec, values)
            result = asyncio.run(dispatch(message))
        except (AppError, OSError, ValueError) as exc:
            raise click.ClickException(str(exc)) from exc
        render(spec, result)

    return callback


async def dispatch(message: Message) -> ServiceResult:
    async with build_client_port() as port:
        return await port.forward(message)
