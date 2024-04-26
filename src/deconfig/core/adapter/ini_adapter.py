import configparser
from typing import Callable, Any, List, Optional, TypeVar

from deconfig.core.adapter.adapter_base import AdapterBase
from deconfig.core.adapter.adapter_error import AdapterError
from deconfig.core.field_util import FieldUtil

T = TypeVar("T")

__version__ = "0.1.0"
__author__ = "ybhaw"
__license__ = "MIT"


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


__all__ = ["IniAdapter"]
