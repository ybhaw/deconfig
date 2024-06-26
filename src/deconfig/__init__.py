"""
Deconfig is a library that allows you to easily manage configuration for your application.
It is decorator driven, which means you can easily add configuration to your class methods.

Example Usage:

```python
from deconfig import config, field, EnvAdapter


@config([EnvAdapter()])
class ExampleConfig:
    @field(name="foo")
    def get_foo(self) -> str:
        return "default"  # Returns value of "FOO" environment variable
```
"""

from typing import Optional, TypeVar, Callable, List, Type

from deconfig.core import FieldUtil, AdapterError, AdapterBase
from deconfig.ini_adapter import IniAdapter
from deconfig.env_adapter import EnvAdapter
from deconfig.__version__ import __version__, __author__, __license__


T = TypeVar("T")
U = TypeVar("U")


def _decorated_config_decorator(getter_function: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that will handle all logic for getting field value.
    """

    # Get decorator values from getter function
    name = FieldUtil.get_name(getter_function)
    adapters = FieldUtil.get_adapters(getter_function)

    optional_ = FieldUtil.is_optional(getter_function)

    def build_response_from_config(*args, **kwargs) -> T:
        """
        Get field value from adapters or getter function.
        """
        for adapter_ in adapters:
            try:
                return adapter_.get_field(name, getter_function, *args, **kwargs)
            except AdapterError:
                continue
        raise AdapterError("Value not found in any config")

    def decorated_config_wrapper(*args, **kwargs) -> T:
        if FieldUtil.has_cached_response(getter_function):
            return FieldUtil.get_cached_response(getter_function)

        try:
            response = build_response_from_config(*args, **kwargs)
        except AdapterError as e:
            if optional_ is False:
                raise ValueError(f"Field {name} not found in any config.") from e
            response = getter_function(*args, **kwargs)
        FieldUtil.set_cached_response(getter_function, response)
        return response

    FieldUtil.set_original_function(decorated_config_wrapper, getter_function)
    return decorated_config_wrapper


def reset_cache(obj: Type[AdapterBase]):
    """
    Reset cache for all fields in the class.
    """
    for name in dir(obj):
        getter_function = getattr(obj, name)
        if not callable(getter_function) or not FieldUtil.has_original_function(
            getter_function
        ):
            continue
        getter_function = FieldUtil.get_original_function(getter_function)
        if FieldUtil.has_cached_response(getter_function):
            FieldUtil.delete_cached_response(getter_function)


def field(name: str) -> Callable[..., T]:
    """
    Decorator for methods that will get field value.
    Example:
        @field(name="foo")
        def get_foo(self) -> Optional[str]:
            return None
    ```
    """

    if name is None:
        raise TypeError("Name is required.")

    try:
        name = str(name)
    except (ValueError, TypeError) as e:
        raise TypeError("Name should be a string.") from e

    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        FieldUtil.set_name(func, name)
        FieldUtil.initialize_adapter_configs(func)
        return func

    return wrapper


def optional(is_optional: bool = True) -> Callable[..., T]:
    """
    Decorator for optional fields. If field is required, but got None, ValueError will be raised.
    """
    try:
        if is_optional or not is_optional:
            pass
    except (ValueError, TypeError) as e:
        raise TypeError("Optional should be a boolean.") from e

    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        FieldUtil.set_optional(func, is_optional)
        return func

    return wrapper


def add_adapter(adapter_: AdapterBase) -> Callable[..., T]:
    """
    Decorator for adding an adapter to the field.
    """

    if adapter_ is None:
        raise TypeError("Adapter is required.")

    if not hasattr(adapter_, AdapterBase.get_field.__name__):
        raise TypeError("Adapter must extend AdapterBase or have get_field method.")

    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        FieldUtil.add_adapter(func, adapter_)
        return func

    return wrapper


_adapters: List[AdapterBase] = [EnvAdapter()]


def set_default_adapters(*adapters: AdapterBase) -> None:
    """Setting default adapters"""
    if len(adapters) == 0:
        raise TypeError("At least one adapter is required.")
    if not all(hasattr(a, AdapterBase.get_field.__name__) for a in adapters):
        raise TypeError("Adapter must extend AdapterBase or have get_field method.")
    global _adapters  # pylint: disable=global-statement
    _adapters = adapters


def config(adapters: Optional[List[AdapterBase]] = None):
    """
    Decorator for the config class.
    """
    if adapters is None:
        adapters = _adapters

    def wrapper(class_: Type[AdapterBase]):
        for name, getter_function in class_.__dict__.items():
            # Skip non-field methods
            if not callable(getter_function) or not FieldUtil.has_name(getter_function):
                continue

            # Field adapters get priority
            field_adapters = adapters
            if FieldUtil.get_adapters(getter_function) is not None:
                field_adapters = [*FieldUtil.get_adapters(getter_function), *adapters]
            FieldUtil.set_adapters(getter_function, field_adapters)

            # Decorate with yield, that will handle all logic
            setattr(class_, name, _decorated_config_decorator(getter_function))

        return class_

    return wrapper


__all__ = [
    "field",
    "optional",
    "add_adapter",
    "set_default_adapters",
    "reset_cache",
    "config",
    # Adapters
    "EnvAdapter",
    "IniAdapter",
]
