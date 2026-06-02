from dataclasses import MISSING, fields
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from stega_core.message import Message


def marshal(msg_type: type[Message], data: dict[str, Any]) -> Message:
    hints = get_type_hints(msg_type)
    kwargs = {}
    missing = []
    for fld in fields(msg_type):
        if fld.name in data:
            kwargs[fld.name] = coerce(data[fld.name], hints[fld.name])
        elif fld.default is not MISSING or fld.default_factory is not MISSING:
            continue
        else:
            missing.append(fld.name)
    if missing:
        err_msg = f"missing required fields: {', '.join(missing)}"
        raise ValueError(err_msg)
    return msg_type(**kwargs)


def coerce(  # noqa: PLR0911
    value: Any,  # noqa: ANN401
    annotation: type,
) -> Any:  # noqa: ANN401
    origin = get_origin(annotation)

    # handle Optional[T] = T | None annotations
    if origin in (Union, UnionType):
        if value is None:
            return None
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        return coerce(value, args[0])

    # handle list[T] annotations
    if origin in (list, list):
        (inner,) = get_args(annotation) or (Any,)
        if not isinstance(value, list):
            err_msg = f"expected list, got {type(value).__name__}"
            raise TypeError(err_msg)
        return [coerce(val, inner) for val in value]

    # handle any/None
    if annotation is Any or annotation is None:
        return value

    # handle booleans
    if annotation is bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    # primitive coercion
    if isinstance(value, annotation):
        return value
    return annotation(value)
