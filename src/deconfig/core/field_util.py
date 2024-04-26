from typing import Callable, Dict, Type, Any, TypeVar, List, Optional

from deconfig.core.adapter.adapter_base import AdapterBase

T = TypeVar("T")


class FieldUtil:
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
    def upsert_adapter_config(cls, function: Callable[..., T], adapter: Type[AdapterBase], config: Any):
        """
        Add adapter to the function.
        """
        adapters = cls.get_adapter_configs(function)
        adapters[adapter] = config
        setattr(function, "adapter_configs", adapters)

    @classmethod
    def has_adapter_configs(cls, function: Callable[..., T]) -> bool:
        return hasattr(function, "adapter_configs")

    @classmethod
    def get_adapters(cls, function: Callable[..., T]) -> Optional[List[AdapterBase]]:
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
        return hasattr(function, "adapters")

    @classmethod
    def add_adapter(cls, function: Callable[..., T], adapter_: AdapterBase) -> None:
        """
        Add adapter to the function.
        """
        adapters = cls.get_adapters(function) or []
        adapters.append(adapter_)
        setattr(function, "adapters", adapters)

    @classmethod
    def set_name(cls, function: Callable[..., T], name: str) -> None:
        """
        Add name to the function.
        """
        setattr(function, "name", name)

    @classmethod
    def has_name(cls, function: Callable[..., T]) -> bool:
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
    def add_validation_callback(cls, function: Callable[..., T], callback: Callable[..., T]) -> None:
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
    def set_cache_response(cls, function: Callable[..., T], response: T) -> None:
        """
        Set cache response to the function.
        """
        setattr(function, "cached_response", response)

    @classmethod
    def has_cache_response(cls, function: Callable[..., T]) -> bool:
        """
        Check if function has cache response.
        """
        return hasattr(function, "cached_response")

    @classmethod
    def get_cache_response(cls, function: Callable[..., T]) -> Optional[T]:
        """
        Get cache response from the function.
        """
        return getattr(function, "cached_response")

    @classmethod
    def delete_cache_response(cls, function: Callable[..., T]) -> None:
        """
        Delete cache response from the function.
        """
        if cls.has_cache_response(function):
            delattr(function, "cached_response")
