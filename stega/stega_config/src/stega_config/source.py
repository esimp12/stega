from __future__ import annotations

import os
import warnings
from abc import ABC, abstractmethod
from enum import Flag
from pathlib import Path
from typing import Any, Final


class UnusedType:

    _instance: UnusedType | None = None

    def __new__(cls) -> UnusedType:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "UNUSED"

    def __reduce__(self):
        return (UnusedType, ())


UNUSED: Final = UnusedType()


class Source(ABC):
    """Base class for defining a config source.

    NOTE: A config source is a way to load config values from different
    sources such as environment variables, files, etc. This class is intended
    to be extended by specific source classes that implement the _source method.

    WARNING: Instances of the Source class (or any children) should not be created
    or called directly by clients. The intended usage is to associate a FrozenConfig
    class attribute with a Source instance, which will then make the appropriate calls
    to load the config value from the given source type using both the class attribute's
    name and type from the known annotations.
    """

    def __init__(self, depends_on: str | None = None, depends_value: Any = None) -> None:
        self._depends_on = depends_on
        self._depends_value = depends_value

    def __call__(
        self,
        field: str,
        rt: type,
        depends_attrs_map: dict[str, Any] | None = None,
        prefix: str | None = None,
    ) -> Any:
        """Calls the source to get the value for a given field."""
        if self._depends_on is not None:
            depends_attrs_map = depends_attrs_map or {}

            if self._depends_on not in depends_attrs_map:
                err_msg = f"'{field}' depends on '{self._depends_on}' but is not resolved"
                raise RuntimeError(err_msg)

            actual = depends_attrs_map[self._depends_on]
            if not self._satisfied(actual):
                return UNUSED

        key = f"{prefix}_{field}" if prefix else field
        val = self._source(key)
        try:
            if rt is bool:
                val = True if _is_truthy(val) else False
            else:
                val = rt(val)
        except (TypeError, ValueError):
            warnings.warn(f"Could not convert value '{val}' to type {rt}. Casting to str.")
            val = str(val)
        return val

    def _satisfied(self, actual: Any) -> bool:
        if isinstance(self._depends_value, Flag) and isinstance(actual, Flag):
            return bool(actual & self._depends_value)
        return actual == self._depends_value

    @abstractmethod
    def _source(self, field: str):
        """Returns the value for a given field from the source."""


class FileSource(Source):
    """Source for loading config values from a file.

    NOTE: The name of the file is the field name and the value is the entire
    contents of the file. The file is expected to be a text file with a single line
    containing the value. If the file does not exist, a FileNotFoundError is raised.
    """

    def __init__(
        self,
        path: str,
        depends_on: str | None = None,
        depends_value: Any = None,
    ) -> None:
        super().__init__(depends_on=depends_on, depends_value=depends_value)
        self.path = path

    def _source(self, field: str):
        path = Path(self.path) / field
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.read_text().strip()


class EnvSource(Source):
    """Source for loading config values from environment variables.

    NOTE: The name of the environment variable is the field name and the value is
    the value of the environment variable. If the environment variable does not exist,
    a KeyError is raised. If the environment variable is set to an empty string,
    the default value will be used instead.
    """

    def __init__(
        self,
        default: Any | None = None,
        depends_on: str | None = None,
        depends_value: Any = None,
    ) -> None:
        super().__init__(depends_on=depends_on, depends_value=depends_value)
        self.default = default

    def _source(self, field: str):
        value = os.getenv(field, self.default)
        if value == "":
            value = self.default # empty string is considered as no value set
        if value is None:
            raise ValueError(f"Default value for '{field}' is not set and no environment variable exists.")
        return value


def source(source_type: str, **kwargs: Any) -> Source:
    """Allows loading a config value based on a given source type.

    All config values will check the environment for a value first, even if
    no 'source()' is identified and just a primitive type is provided. This allows
    for easy overriding of config values at runtime without having to specify an
    'env' source for every config value. Other source types require explicit call outs
    (e.g. 'source("file", path="/path/to/file")').

    NOTE: The following source types are supported:
        - file: Loads the config value from a file at the given path.
        - env: Loads the config value from an environment variable.

    Args:
        source_type: A string of the type of source to load the config value from.
        **kwargs: Additional arguments to pass based on the source type.

    Returns:
        source: A Source instance for the given source type.

    """
    depends_on = kwargs.pop("depends_on", None)
    depends_value = kwargs.pop("depends_value", None)
    if (depends_on is None) != (depends_value is None):
        err_msg = "depends_on and depends_value must be provided together"
        raise ValueError(err_msg)
    depends = {"depends_on": depends_on, "depends_value": depends_value}

    if source_type == "file":
        if "path" not in kwargs:
            raise ValueError("FileSource requires a 'path' argument.")
        return FileSource(**kwargs, **depends)
    if source_type == "env":
        if "default" in kwargs:
            return EnvSource(**kwargs, **depends)
        return EnvSource(**depends)
    raise ValueError(f"Unknown source type: {source_type}")
