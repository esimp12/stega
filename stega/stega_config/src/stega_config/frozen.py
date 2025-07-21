"""Module for defining immutable configs."""

from __future__ import annotations

import inspect
import os
import typing as T
import warnings
from pathlib import Path


class Source:
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

    def __call__(self, field: str, rt: type) -> T.Any:
        """Calls the source to get the value for a given field."""
        val = self._source(field)
        try:
            if rt is bool:
                val = True if _is_truthy(val) else False
            else:
                val = rt(val)
        except (TypeError, ValueError):
            warnings.warn(f"Could not convert value '{val}' to type {rt.__name__}. Casting to str.")
            val = str(val)
        return val

    def _source(self, field: str, rt: type):
        """Returns the value for a given field from the source."""
        raise NotImplementedError("Subclasses must implement this method.")


class FileSource(Source):
    """Source for loading config values from a file.

    NOTE: The name of the file is the field name and the value is the entire
    contents of the file. The file is expected to be a text file with a single line
    containing the value. If the file does not exist, a FileNotFoundError is raised.
    """

    def __init__(self, path: str):
        super().__init__()
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

    def __init__(self, default: T.Any | None = None):
        super().__init__()
        self.default = default

    def _source(self, field: str):
        value = os.getenv(field, self.default)
        if value == "":
            value = self.default # empty string is considered as no value set
        if value is None:
            raise ValueError(f"Default value for '{field}' is not set and no environment variable exists.")
        return value


def source(source_type, **kwargs) -> Source:
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
    if source_type == "file":
        if "path" not in kwargs:
            raise ValueError("FileSource requires a 'path' argument.")
        return FileSource(**kwargs)
    if source_type == "env":
        if "default" in kwargs:
            return EnvSource(**kwargs)
        return EnvSource()
    raise ValueError(f"Unknown source type: {source_type}")


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

    def __init__(self, mapping: dict | None = None):
        """Inits FrozenConfig.

        After first initialization any class or instance attributes on the config
        become immutable.

        Args:
            mapping: A dict of initial values to set for the config.

        """
        if mapping is None:
            mapping = {}
        self.__data = {}
        for key, value in mapping.items():
            self.__data[key] = value

        if not getattr(self.__class__, "__frozen"):
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

                # At this point we should always have a Source instance, we call it to load the actual
                # config value. Note this automatically handles type casting based on the config class
                # type annotation.
                if isinstance(cls_attr_value, Source):
                    cls_attr_value = cls_attr_value(cls_attr, cls_attr_rt)

                # NOTE: The below works, but I believe the original intention was to 'remove' any class attributes
                # and essentially force any config access to go through the __data dict. The problem was that
                # we were only removing class level attributes of FrozenConfig but we had multiple parent class
                # layers between the child config class actually used and this FrozenConfig class (e.g.
                # FrozenConfig -> BaseConfig -> PortfolioConfig -> ProdConfig). I believe if we defined a class
                # attribute on the PortfolioConfig class it would never be removed even if overridden by an
                # environment variable. And so if a child class (e.g. ProdConfig) didn't overwrite that class
                # attribute but at runtime we wanted to set the value, it would only look to the parent class for
                # accessing that attribute (e.g. see super().__getattribute__(name) in the metaclass above) which
                # may be completely different than what the user set at runtime.

                # And so, maybe the 'right' solution is to walk up the class hierarchy and remove the given class
                # attribute from all parent classes up the chain. Then we would default to only accessing the class
                # attribute via the __data dict. The question remains whether removing all of the class attributes
                # actually allows class level access to work. I think the answer is yes, because the metaclass
                # __call__ method forces the class to be instantiated as a singleton and so the __data dict would
                # get populated, but am not sure. This proposed solution is straightforward enough to introduce
                # (e.g. for cls in cls.__mro__ ...), but am leaving as a TODO for now given that the solution below
                # works (we just set the class attribute directly on the config class) and we can always change
                # it later if needed.

                # TODO: Explore above and see if it works as expected.
                setattr(self.__class__, cls_attr, cls_attr_value)

                # Control config attribute access via __data
                self.__data[cls_attr] = cls_attr_value

        # Do not allow any modification at this point
        setattr(self.__class__, "__frozen", True)

    def __setitem__(self, key: str, value: T.Any) -> None:
        """Sets the value for a FrozenConfig attribute.

        Args:
            key: A string of the name of the instance attribute.
            value: The value to set for the instance attribute.

        """
        self.__setattr__(key, value)

    def __setattribute__(self, name: str, value: T.Any) -> None:
        """Sets the value for a FrozenConfig attribute.

        Args:
            name: A string of the name of the instance attribute.
            value: The value to set for the instance attribute.

        """
        self.__setattr__(name, value)

    def __setattr__(self, name: str, value: T.Any) -> None:
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

    def __getitem__(self, key: str) -> T.Any:
        """Gets the value for a FrozenConfig attribute.

        Args:
            key: A string of the name of the instance attribute.

        Returns:
            The value of the instance attribute.

        """
        return self.__getattr__(key)

    def __getattr__(self, name: str) -> T.Any:
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

    def get_envvars(self) -> T.Sequence[tuple[str, T.Any]]:
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
    # Collect all possible public class annotations of the config class up the
    # inheritance chain until we get to the BaseConfig class.
    if len(cls.__bases__) == 0:
        return []

    attrs = set()
    annotations = []
    current_cls = cls
    parent_cls = current_cls.__bases__[0]
    while parent_cls is not BaseConfig:
        current_annotations = [
            (attr, rt) for attr, rt in inspect.get_annotations(current_cls).items() if attr not in attrs
        ]
        annotations.extend(current_annotations)
        attrs.update(attr for attr, _ in current_annotations)
        current_cls = parent_cls
        if len(current_cls.__bases__) == 0:
            break
        parent_cls = current_cls.__bases__[0]

    # Add the last BaseConfig child class annotations
    if parent_cls is BaseConfig:
        annotations.extend((attr, rt) for attr, rt in inspect.get_annotations(current_cls).items() if attr not in attrs)

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


# TODO: Move this to stega_lib
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
