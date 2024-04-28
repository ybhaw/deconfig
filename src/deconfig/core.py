"""
Core module for deconfig.
These can be used to create custom adapters, or to modify behavior of the library.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional
from typing import Callable, TypeVar
from typing import Dict, Type


T = TypeVar("T")


class AdapterError(Exception):
    """
    Raised when adapter fails to get field value.
    """


# pylint: disable=too-few-public-methods
class AdapterBase(ABC):
    """
    Base class for all adapters.
    """

    @abstractmethod
    def get_field(
            self, field_name: str, method: Callable[..., T], *method_args, **method_kwargs
    ) -> Any:
        """
        Use this method to initialize the field in configuration.
        If field is not present in config, AdapterError should be
        raised to indicate to library to try next adapter.

        :param field_name: Field name as passed in @field
        :param method: getter method, use with FieldUtil to get config properties
        :param method_args: Arguments passed to getter method
        :param method_kwargs: Keyword arguments passed to getter method
        :return: Value if field is present, otherwise raise AdapterError
        :raises AdapterError: If field is not present, this indicates to library to try next adapter
        """


# pylint: disable=too-many-public-methods
class FieldUtil:
    """
    Utility class for managing field properties.
    These properties are how the library knows how to get the field value.
    """

    @classmethod
    def get_adapter_configs(cls, function: Callable[..., T]) -> Dict[Type[AdapterBase], Any]:
        """
        Get adapter list from function.
        """
        if not hasattr(function, "adapter_configs"):
            raise ValueError("Please decorate the class with @config.")
        return getattr(function, "adapter_configs")

    @classmethod
    def initialize_adapter_configs(cls, function: Callable[..., T]):
        """
        Set adapter list to function.
        """
        setattr(function, "adapter_configs", {})

    @classmethod
    def upsert_adapter_config(
            cls, function: Callable[..., T], adapter: Type[AdapterBase], config: Any
    ):
        """
        Add adapter to the function.
        """
        adapters = cls.get_adapter_configs(function)
        adapters[adapter] = config
        setattr(function, "adapter_configs", adapters)

    @classmethod
    def get_adapters(cls, function: Callable[..., T]) -> Optional[List[AdapterBase]]:
        """
        Get adapter list from function of @config() class
        """
        if not hasattr(function, "adapters"):
            return None
        return getattr(function, "adapters")

    @classmethod
    def set_adapters(cls, function: Callable[..., T], adapters: List[AdapterBase]) -> None:
        """
        Set adapter list to function.
        """
        setattr(function, "adapters", adapters)

    @classmethod
    def has_adapters(cls, function: Callable[..., T]) -> bool:
        """
        Check if function has adapters.
        """
        return hasattr(function, "adapters")

    @classmethod
    def add_adapter(cls, function: Callable[..., T], adapter_: AdapterBase) -> None:
        """
        Add adapter to the function.
        """
        adapters = cls.get_adapters(function) or []
        adapters.insert(0, adapter_)
        cls.set_adapters(function, adapters)

    @classmethod
    def set_name(cls, function: Callable[..., T], name: str) -> None:
        """
        Add name to the function.
        """
        setattr(function, "name", name)

    @classmethod
    def has_name(cls, function: Callable[..., T]) -> bool:
        """
        Check if function has name set using @field decorator.
        """
        return hasattr(function, "name")

    @classmethod
    def get_name(cls, function: Callable[..., T]) -> str:
        """
        Get name from the function.
        """
        try:
            return getattr(function, "name")
        except AttributeError as e:
            raise ValueError("Please decorate the field with @name.") from e

    @classmethod
    def add_validation_callback(
            cls, function: Callable[..., T], callback: Callable[..., T]
    ) -> None:
        """
        Add validation callback to the function.
        """
        setattr(function, "validation_callback", callback)

    @classmethod
    def get_validation_callback(cls, function: Callable[..., T]) -> Optional[Callable[..., T]]:
        """
        Get validation callback from the function.
        """
        return getattr(function, "validation_callback", None)

    @classmethod
    def set_optional(cls, function: Callable[..., T], is_optional: bool = True) -> None:
        """
        Set optional to the function.
        """
        setattr(function, "optional", is_optional)

    @classmethod
    def is_optional(cls, function: Callable[..., T]) -> bool:
        """
        Get optional from the function.
        """
        return getattr(function, "optional", False)

    @classmethod
    def add_transform_callback(cls, function: Callable[..., T], callback: Callable[..., T]) -> None:
        """
        Add transform callback to the function.
        """
        setattr(function, "transform_callback", callback)

    @classmethod
    def get_transform_callback(cls, function: Callable[..., T]) -> Optional[Callable[..., T]]:
        """
        Get transform callback from the function.
        """
        return getattr(function, "transform_callback", None)

    @classmethod
    def set_cached_response(cls, function: Callable[..., T], response: T) -> None:
        """
        Set cache response to the function.
        """
        setattr(function, "cached_response", response)

    @classmethod
    def has_cached_response(cls, function: Callable[..., T]) -> bool:
        """
        Check if function has cache response.
        """
        return hasattr(function, "cached_response")

    @classmethod
    def get_cached_response(cls, function: Callable[..., T]) -> Optional[T]:
        """
        Get cache response from the function.
        """
        if not cls.has_cached_response(function):
            raise ValueError("Cache response not found.")
        return getattr(function, "cached_response")

    @classmethod
    def delete_cached_response(cls, function: Callable[..., T]) -> None:
        """
        Delete cache response from the function.
        """
        if cls.has_cached_response(function):
            delattr(function, "cached_response")

    @classmethod
    def set_original_function(
            cls, wrapper_function: Callable[..., T], original_function: Callable[..., T]
    ) -> None:
        """
        Set original function to the wrapper function.
        """
        setattr(wrapper_function, "original_function", original_function)

    @classmethod
    def get_original_function(cls, wrapper_function: Callable[..., T]) -> Callable[..., T]:
        """
        Get original function from the wrapper function.
        """
        if not cls.has_original_function(wrapper_function):
            raise ValueError("Original function not found.")
        return getattr(wrapper_function, "original_function")

    @classmethod
    def has_original_function(cls, wrapper_function: Callable[..., T]) -> bool:
        """
        Check if function has original function.
        """
        return hasattr(wrapper_function, "original_function")
