"""Module for defining immutable configs."""

from __future__ import annotations

import inspect
import os
import typing as T


class FrozenConfigMeta(type):
    """Metaclass for forcing class attributes to be immutable.

    Attributes:
        __frozen: A boolean for locking the instance as immutable after initialization.
        __instances: A dict for creating unique config instances.
    """

    __frozen: bool = False
    __instances: T.Dict = {}

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
        cls.__setattr__(key, value)  # pylint: disable=no-value-for-parameter

    def __setattribute__(cls, name: str, value: T.Any):
        """Sets the value for a FrozenConfig class attribute.

        Args:
            name: A string of the name of the class attribute.
            value: The value to set for the class attribute.
        """
        cls.__setattr__(name, value)  # pylint: disable=no-value-for-parameter

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
        return cls.__getattr__(key)  # pylint: disable=no-value-for-parameter

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

    def __init__(self, mapping: T.Optional[T.Dict] = None):
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
            for cls_attr in get_public_class_attributes(self.__class__):
                # Get config value from environment if exists otherwise use default
                # class attribute
                cls_attr_value = os.getenv(cls_attr, getattr(self.__class__, cls_attr))

                # Delete config class attribute to defer access to private __data access
                if hasattr(FrozenConfig, cls_attr):
                    delattr(FrozenConfig, cls_attr)

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
            raise AttributeError(
                f"Cannot set class attributes of {self.__class__.__name__}!"
            )
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


def get_public_class_attributes(cls):
    """Gets the public class attributes of a given class.

    Args:
        cls: A class to find the public attributes for.

    Returns:
        A list of class attribute names.
    """
    base_attrs = dir(type("", (object,), {}))
    return [
        attr
        for attr, _ in inspect.getmembers(cls)
        if attr not in base_attrs
        and not callable(getattr(cls, attr))
        and not attr.startswith("__")  # exclude dunder methods and private attributes
    ]


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
