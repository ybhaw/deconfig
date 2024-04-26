from typing import Optional, TypeVar, Callable, List, Type

from deconfig.core import FieldUtil, AdapterError, AdapterBase, EnvAdapter, IniAdapter
from deconfig.transformer import transform
from deconfig.__version__ import __version__

__author__ = "ybhaw"
__license__ = "MIT"


T = TypeVar("T")
U = TypeVar("U")


def decorated_config_decorator(getter_function: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that will handle all logic for getting field value.
    """

    # Get decorator values from getter function
    if not FieldUtil.has_name(getter_function):
        raise ValueError("Have you forgotten to decorate field with @field(name='name')?")
    name = FieldUtil.get_name(getter_function)

    if not FieldUtil.has_adapters(getter_function):
        raise ValueError("Class not decorated with @config")
    adapters = FieldUtil.get_adapters(getter_function)

    optional_ = FieldUtil.is_optional(getter_function)
    validation_callback_ = FieldUtil.get_validation_callback(getter_function)
    transform_callback_ = FieldUtil.get_transform_callback(getter_function)

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
        if FieldUtil.has_cache_response(getter_function):
            return FieldUtil.get_cache_response(getter_function)

        try:
            response = build_response_from_config(*args, **kwargs)
        except AdapterError as e:
            if optional_ is False:
                raise ValueError(f"Field {name} not found in any config.") from e
            else:
                response = getter_function(*args, **kwargs)
        if transform_callback_ is not None:
            response = transform_callback_(response)
        if optional_ is False and response is None:
            raise ValueError(f"Field {name} not found in any config.")
        if validation_callback_ is not None:
            validation_callback_(response)
        FieldUtil.set_cache_response(getter_function, response)
        return response
    FieldUtil.set_original_function(decorated_config_wrapper, getter_function)
    return decorated_config_wrapper


def _reset_cache(obj: T) -> T:
    """
    Decorator values are cached. This method will reset cache for all fields.
    """
    for name in dir(obj):
        getter_function = getattr(obj, name)
        if not callable(getter_function) or not FieldUtil.has_original_function(getter_function):
            continue
        getter_function = FieldUtil.get_original_function(getter_function)
        if FieldUtil.has_cache_response(getter_function):
            FieldUtil.delete_cache_response(getter_function)
    return obj


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


def validate(callback: Callable[..., None]) -> Callable[..., T]:
    """
    Decorator for adding a validation callback.
    Validation callback will be called after field value is retrieved.
    """
    if callback is None:
        raise TypeError("Callback argument is required.")

    if not callable(callback):
        raise TypeError("Callback must be a callable.")

    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        FieldUtil.add_validation_callback(func, callback)
        return func
    return wrapper


def add_adapter(adapter_: AdapterBase) -> Callable[..., T]:
    """
    Decorator for adding an adapter to the field.
    """

    if adapter_ is None:
        raise TypeError("Adapter is required.")

    if not hasattr(adapter_, AdapterBase.get_field.__name__):
        raise TypeError(f"Adapter must extend AdapterBase or have get_field method")

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
        raise TypeError("All adapters must be instance of AdapterBase.")
    global _adapters
    _adapters = adapters


def config(adapters: Optional[List[AdapterBase]] = None):
    """
    Decorator for the config class.
    """
    global _adapters
    if adapters is None:
        adapters = _adapters

    def wrapper(class_: Type[AdapterBase]):
        for name, getter_function in class_.__dict__.items():
            # Skip non-field methods
            if not callable(getter_function) or not FieldUtil.has_name(getter_function):
                continue

            if not FieldUtil.has_adapter_configs(getter_function):
                FieldUtil.initialize_adapter_configs(getter_function)

            # Field adapters get priority
            field_adapters = adapters
            if FieldUtil.get_adapters(getter_function) is not None:
                field_adapters = [*FieldUtil.get_adapters(getter_function), *adapters]
            FieldUtil.set_adapters(getter_function, field_adapters)

            # Decorate with yield, that will handle all logic
            setattr(class_, name, decorated_config_decorator(getter_function))

        # Add method to reset cache for all fields
        if not hasattr(class_, "reset_deconfig_cache"):
            setattr(class_, "reset_deconfig_cache", _reset_cache)
        return class_
    return wrapper


__all__ = [
    "field",
    "optional",
    "validate",
    "add_adapter",
    "set_default_adapters",
    "config",

    # Transformers
    "transform",

    # Adapters
    "EnvAdapter",
    "IniAdapter",
]
