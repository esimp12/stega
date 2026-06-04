"""Module for defining immutable configs."""

from __future__ import annotations

import inspect
import warnings
from typing import Any

from stega_config.source import Source, source


class FrozenConfigMeta(type):
    """Metaclass for forcing class attributes to be immutable.

    Attributes:
        __frozen: A boolean for locking the instance as immutable after initialization.
        __instances: A dict for creating unique config instances.

    """
    __frozen: bool = False
    __instances: dict = {}

    def __new__(mcs, name, bases, dct):
        """Creates a new frozen config class.

        Args:
            name: A string of the name of the class.
            bases: A tuple of the base classes for the given class.
            dct: A dict of the kwargs used to create the given class.

        Returns:
            A copy of a frozen config class with the current immutability state.

        """
        dct["__frozen"] = mcs.__frozen
        return super().__new__(mcs, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        """Calls a cached instance of a frozen config instance.

        Args:
            *args: Args to supply to config initialization.
            **kwargs: Kwargs to supply to config initialization.

        Returns:
            A FrozenConfig instance.

        """
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]

    def __setitem__(cls, key: str, value: T.Any):
        """Sets the value for a FrozenConfig class attribute.

        Args:
            key: A string of the name of the class attribute.
            value: The value to set for the class attribute.

        """
        cls.__setattr__(key, value)

    def __setattribute__(cls, name: str, value: T.Any):
        """Sets the value for a FrozenConfig class attribute.

        Args:
            name: A string of the name of the class attribute.
            value: The value to set for the class attribute.

        """
        cls.__setattr__(name, value)

    def __setattr__(cls, name: str, value: T.Any) -> None:
        """Sets the value for a FrozenConfig class attribute.

        Args:
            name: A string of the name of the class attribute.
            value: The value to set for the class attribute.

        Raises:
            An AttributeError if the frozen config class is immutable at this point.

        """
        if getattr(cls, "__frozen"):
            raise AttributeError(f"Cannot set class attributes of {cls.__name__}!")
        super().__setattr__(name, value)

    def __getitem__(cls, key: str) -> T.Any:
        """Gets the value for a FrozenConfig class attribute.

        Args:
            key: A string of the name of the class attribute.

        Returns:
            The value of the class attribute.

        """
        return cls.__getattr__(key)

    def __getattr__(cls, name: str) -> T.Any:
        """Gets the value for a FrozenConfig class attribute.

        Args:
            name: A string of the name of the class attribute.

        Raises:
            An AttributeError if access to a private class attribute is attempted.

        Returns:
            The value of the class attribute.

        """
        if getattr(cls, "__frozen") and name not in get_private_class_attributes(cls):
            raise AttributeError(f"Cannot get class attributes of {cls.__name__}!")
        return super().__getattribute__(name)


class FrozenConfig(metaclass=FrozenConfigMeta):
    """Creates a config instance with immutable attributes.

    Attempts to load class attributes from current environment variables if they exist,
    otherwise uses whatever default value is supplied.

    Attributes:
        __data: A dict of key value config values kept for the class.

    """

    __prefix__: ClassVar[str | None] = None

    def __init__(self, mapping: dict | None = None):
        """Inits FrozenConfig.

        After first initialization any class or instance attributes on the config
        become immutable.

        Args:
            mapping: A dict of initial values to set for the config.

        """
        # check if config is already frozen
        if getattr(self.__class__, "__frozen"):
            return

        # initial mapping to set for config
        if mapping is None:
            mapping = {}
        self.__data = {}
        for key, value in mapping.items():
            self.__data[key] = value

        # get prefix once
        prefix = getattr(self.__class__, "__prefix__", None)

        triples = []
        for cls_attr, cls_attr_rt in get_class_config_annotations(self.__class__):
            # NOTE: A class attribute may not have a default value because it is expected
            # or required to be set at runtime. If this is the case, then we warn the
            # user that it is not set but still allow it to be set to None.
            try:
                cls_attr_value = getattr(self.__class__, cls_attr)
            except AttributeError:
                cls_attr_value = None
                warnings.warn(
                    f"Config attribute '{cls_attr}' not found in class '{self.__class__.__name__}',"
                    " using None as default value.",
                )
                
            # If the class attribute is not a Source instance, we still assume a user will want to
            # set the value at runtime, but default to only check an environment variable. And so,
            # we recreate the class attribute as a EnvSource instance with the default value given
            # by the actual class attribute value.
            if not isinstance(cls_attr_value, Source):
                cls_attr_value = source("env", default=cls_attr_value)

            triples.append((cls_attr, cls_attr_rt, cls_attr_value))

        # build sources that are dependencies for other sources
        depended_on = {
            src._depends_on
            for _, _, src in triples
            if src._depends_on is not None
        }
        depends_attrs_map: dict[str, Any] = {}

        # resolve depended on sources first
        for attr, rt, src in triples:
            if attr not in depended_on:
                continue
            if src._depends_on is not None:
                err_msg = f"'{attr}' may not depend on itself"
                raise RuntimeError(err_msg)
            value = src(field=attr, rt=rt, prefix=prefix)
            depends_attrs_map[attr] = value
            setattr(self.__class__, attr, value)
            self.__data[attr] = value

        # resolve all other sources
        for attr, rt, src in triples:
            if attr in depended_on:
                continue
            value = src(
                field=attr,
                rt=rt,
                depends_attrs_map=depends_attrs_map,
                prefix=prefix,
            )
            setattr(self.__class__, attr, value)
            self.__data[attr] = value

        # do not allow any modification at this point
        setattr(self.__class__, "__frozen", True)

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets the value for a FrozenConfig attribute.

        Args:
            key: A string of the name of the instance attribute.
            value: The value to set for the instance attribute.

        """
        self.__setattr__(key, value)

    def __setattribute__(self, name: str, value: Any) -> None:
        """Sets the value for a FrozenConfig attribute.

        Args:
            name: A string of the name of the instance attribute.
            value: The value to set for the instance attribute.

        """
        self.__setattr__(name, value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Sets the value for a FrozenConfig attribute.

        Args:
            name: A string of the name of the instance attribute.
            value: The value to set for the instance attribute.

        Raises:
            An AttributeError if setting the __frozen attribute is attempted.

        """
        if getattr(self.__class__, "__frozen"):
            raise AttributeError(f"Cannot set class attributes of {self.__class__.__name__}!")
        super().__setattr__(name, value)

    def __getitem__(self, key: str) -> Any:
        """Gets the value for a FrozenConfig attribute.

        Args:
            key: A string of the name of the instance attribute.

        Returns:
            The value of the instance attribute.

        """
        return self.__getattr__(key)

    def __getattr__(self, name: str) -> Any:
        """Gets the value for a FrozenConfig attribute.

        Args:
            name: A string of the name of the instance attribute.

        Returns:
            The value of the instance attribute.

        """
        if name == "__data":
            return self.__data
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        return self.__data[name]


class BaseConfig(FrozenConfig):
    """See FrozenConfig.

    Attributes:
        __CONFIGS: A dict of config names to config classes.

    """

    __CONFIGS: dict[str, FrozenConfigMeta] = {}

    def __init_subclass__(cls, *args, **kwargs):
        """Registers subclass config.

        Args:
            *args: Args to supply to config subclass initialization.
            **kwargs: Kwargs to supply to config subclass initialization.

        Returns:
            A BaseConfig subclass.

        """
        cls.__CONFIGS[cls.__name__] = cls
        return super().__init_subclass__(*args, **kwargs)

    def __repr__(self) -> str:
        """Returns a string representation of the config."""
        envvars = sorted(self.get_envvars(), key=lambda item: item[0])
        envvars = ",\n".join(f"\t{k}={v!r}" for k, v in envvars)
        return f"""{self.__class__.__name__}(\n{envvars}\n)"""

    def get_envvars(self) -> T.Sequence[tuple[str, Any]]:
        """Returns a sequence of environment variables defined in the config."""
        envvars = []
        for k, v in self.items():
            if k.startswith("_"):
                continue
            if isinstance(v, property):
                continue
            envvars.append((k, v))
        return envvars

    @classmethod
    def create_config(cls, env: str) -> BaseConfig:
        """Creates a config from a environment name key.

        Args:
            env: A string of the name of the config environment to load.

        Returns:
            A BaseConfig instance.

        """
        env = env.title()
        config = cls.__CONFIGS.get(f"{env}Config", BaseConfig)
        if config is None:
            raise ValueError(f"{env} not a valid config")
        return config()  # type: ignore


def get_class_config_annotations(cls):
    """Gets the public class config annotations of a given class.

    NOTE: This only retrieves class level attributes that are annotated
    at the class level. This is intended to only be used for config style
    class definitions and not for general data structure classes.

    Args:
        cls: A class to find the public config attributes for.

    Returns:
        A list of class config annotation pairs.

    """
    annotations = []
    seen = set()
    for klass in cls.__mro__:
        if klass in (BaseConfig, object):
            continue
        private_class_attrs = get_private_class_attributes(klass)
        for attr, rt in inspect.get_annotations(klass).items():
            if attr in seen or attr in private_class_attrs:
                continue
            seen.add(attr)
            annotations.append((attr, rt))
    return annotations


def get_private_class_attributes(cls):
    """Gets the private class attributes of a given class.

    Args:
        cls: A class to find the private attributes for.

    Returns:
        A list of class attribute names.

    """
    base_attrs = dir(type("", (object,), {}))
    return [
        attr
        for attr, _ in inspect.getmembers(cls)
        if attr not in base_attrs
        and not callable(getattr(cls, attr))
        and attr.startswith("__")  # include dunder methods and private attributes
    ]


def _is_truthy(value: bool | int | str) -> bool:
    """Checks if a value is truthy or not.

    NOTE: The inputs below have the following truthy values (all str values
    are considered case insensitive):
        - 1         (int) - True
        - "1"       (str) - True
        - "on"      (str) - True
        - "yes"     (str) - True
        - "true"    (str) - True
        - "enabled" (str) - True

        - 0             (int) - False
        - "0"           (str) - False
        - "off"         (str) - False
        - "no"          (str) - False
        - "false"       (str) - False
        - "disabled"    (str) - False
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        value = value.strip().lower()
        return value in {"1", "on", "yes", "true", "enabled"}
    return False  # Default to False for any other type
