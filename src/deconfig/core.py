import configparser
import os
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from typing import Callable, TypeVar
from typing import Dict, Type


T = TypeVar("T")


class AdapterError(Exception):
    """
    Raised when adapter fails to get field value.
    """
    pass


class AdapterBase(ABC):
    """
    Base class for all adapters.
    """

    @abstractmethod
    def get_field(self, field_name: str, method: Callable[..., T], *method_args, **method_kwargs) -> Any:
        """
        Use this method to initialize the field in configuration.
        If field is not present in config, AdapterError should be raised to indicate to library to try next adapter.

        :param field_name: Field name as passed in @field
        :param method: getter method - Use with FieldUtil to get additional properties from the field
        :param method_args: In case the response of getter is a method, arguments passed will be passed to the method
        :param method_kwargs: Same as method_args
        :return: Value if field is present, otherwise raise AdapterError
        :raises AdapterError: If field is not present, this indicates to library to try next adapter
        """
        pass


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

    @classmethod
    def set_original_function(cls, wrapper_function: Callable[..., T], original_function: Callable[..., T]) -> None:
        """
        Set original function to the wrapper function.
        """
        setattr(wrapper_function, "original_function", original_function)

    @classmethod
    def get_original_function(cls, wrapper_function: Callable[..., T]) -> Callable[..., T]:
        """
        Get original function from the wrapper function.
        """
        return getattr(wrapper_function, "original_function")

    @classmethod
    def has_original_function(cls, wrapper_function: Callable[..., T]) -> bool:
        """
        Check if function has original function.
        """
        return hasattr(wrapper_function, "original_function")


class _EnvAdapterConfig:
    def __init__(self):
        self.name: Optional[str] = None
        self.override_prefix: bool = False


class EnvAdapter(AdapterBase):
    """
    Adapter for getting field value from environment variables.
    You can specify environment variable name with @EnvAdapter.name decorator,
    or use field name in uppercase as environment variable name.

    :param env_prefix: Prefix for environment variable names.
    """

    @staticmethod
    def name(name: str, override_prefix: bool = False):
        """
        Decorator for setting environment variable name.

        :param name: Environment variable name.
        :param override_prefix: Override prefix for environment variable name.
        """

        def wrapper(func):
            env_config = FieldUtil.get_adapter_configs(func).get(EnvAdapter, _EnvAdapterConfig())
            env_config.name = name
            env_config.override_prefix = override_prefix
            FieldUtil.upsert_adapter_config(func, EnvAdapter, env_config)
            return func

        return wrapper

    def __init__(self, env_prefix: str = ""):
        self._env_prefix = env_prefix

    def get_field(self, field_name: str, method: Callable[..., T], *args, **kwargs) -> str:
        env_config: Optional[_EnvAdapterConfig] = FieldUtil.get_adapter_configs(method).get(EnvAdapter)

        env_name = field_name.upper()
        if env_config and env_config.name is not None:
            env_name = env_config.name

        prefix = self._env_prefix
        if env_config and env_config.override_prefix:
            prefix = ""

        env_name = prefix + env_name
        if env_name not in os.environ:
            raise AdapterError(f"Environment variable {env_name} not found.")
        return os.environ[env_name]


class _IniAdapterConfig:
    def __init__(self):
        self.name: Optional[str] = None
        self.section_name: Optional[str] = None
        self.file_paths: List[str] = []


class IniAdapter(AdapterBase):
    _ini_adapter_default_paths: Optional[List[str]] = None

    @staticmethod
    def name(
        name: str,
        section_name: Optional[str] = None,
        file_paths: Optional[str] = None,
    ):
        def decorator(func: Callable[..., T]):
            adapters = FieldUtil.get_adapter_configs(func)
            config = adapters.get(IniAdapter, _IniAdapterConfig())
            config.name = name
            config.section_name = section_name
            config.file_paths = file_paths
            FieldUtil.upsert_adapter_config(func, IniAdapter, config)
            return func

        return decorator

    @classmethod
    def with_default_paths(cls, file_paths: List[str]):
        cls._ini_adapter_default_paths = file_paths

    def __init__(self, section_name: str, file_names: Optional[List[str]] = None):
        if file_names is None and self._ini_adapter_default_paths is None:
            raise ValueError("No file paths provided. Either pass file_names or set default using with_default_paths.")
        self.file_names = file_names or self._ini_adapter_default_paths
        self.section_name = section_name
        self.configparser = configparser.ConfigParser()
        self.configparser.read(self.file_names)

    def get_field(self, field_name: str, method: Callable[..., T], *method_args, **method_kwargs) -> Any:
        section_name = self.section_name
        file_paths = self.file_names
        name = field_name
        configparser_ = self.configparser

        ini_config: _IniAdapterConfig = FieldUtil.get_adapter_configs(method).get(IniAdapter)
        if ini_config is not None:
            section_name = ini_config.section_name or section_name
            name = ini_config.name or name
            if ini_config.file_paths is not None:
                configparser_ = configparser.ConfigParser()
                configparser_.read(ini_config.file_paths)

        try:
            return configparser_.get(section_name, name)
        except configparser.NoOptionError:
            raise AdapterError(f"Field {name} not found in {section_name} section of {file_paths}")
