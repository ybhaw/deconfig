import configparser
import logging
from typing import Optional, List, Callable, Any, TypeVar

from deconfig.core import AdapterBase, FieldUtil, AdapterError


T = TypeVar("T")
logger = logging.getLogger(__name__)


class _IniAdapterConfig:
    def __init__(self):
        self.option_name: Optional[str] = None
        self.section_name: Optional[str] = None
        self.file_paths: Optional[List[str]] = None
        self.override_files: bool = True


class IniAdapter(AdapterBase):
    _ini_adapter_default_paths: Optional[List[str]] = None

    @staticmethod
    def configure(
        *,
        option_name: Optional[str] = None,
        section_name: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        override_files: bool = False,
    ):
        def decorator(func: Callable[..., T]):
            adapters = FieldUtil.get_adapter_configs(func)
            config: _IniAdapterConfig = adapters.get(IniAdapter, _IniAdapterConfig())
            config.option_name = option_name
            config.section_name = section_name
            config.file_paths = file_paths
            config.override_files = override_files
            FieldUtil.upsert_adapter_config(func, IniAdapter, config)
            return func

        return decorator

    @classmethod
    def set_default_ini_files(cls, file_paths: List[str]) -> None:
        cls._ini_adapter_default_paths = file_paths

    def __init__(
            self,
            section_name: str,
            file_names: Optional[List[str]] = None,
            override_files: bool = False
    ):
        self.file_names: Optional[List[str]] = file_names
        self.section_name: str = section_name
        self.override_files: bool = override_files
        if self.file_names is None and self._ini_adapter_default_paths is None:
            logger.warning("No INI files specified for IniAdapter")

    def _get_file_names(
            self,
            configuration_file_names: Optional[List[str]] = None,
            configuration_override_files_flag: bool = False,
    ) -> List[str]:
        ini_files = []
        if self._ini_adapter_default_paths is not None:
            ini_files.extend(self._ini_adapter_default_paths)
        if self.override_files is True:
            ini_files = []
        if self.file_names is not None:
            ini_files.extend(self.file_names)
        if configuration_override_files_flag is True:
            ini_files = []
        if configuration_file_names is not None:
            ini_files.extend(configuration_file_names)
        if len(ini_files) == 0:
            raise ValueError("No INI files specified for IniAdapter")
        return ini_files

    def get_field(self, field_name: str, method: Callable[..., T], *method_args, **method_kwargs) -> Any:
        section_name = self.section_name
        option_name = field_name

        ini_config: _IniAdapterConfig = FieldUtil.get_adapter_configs(method).get(IniAdapter)
        if ini_config is not None:
            section_name = ini_config.section_name or section_name
            option_name = ini_config.option_name or option_name
            file_paths = self._get_file_names(ini_config.file_paths, ini_config.override_files)
        else:
            file_paths = self._get_file_names()

        configparser_ = configparser.ConfigParser()
        configparser_.read(file_paths)

        if section_name is None:
            raise ValueError("No section name specified for IniAdapter")

        try:
            return configparser_.get(section_name, option_name)
        except configparser.NoOptionError:
            raise AdapterError(f"Field {option_name} not found in {section_name} section of {file_paths}")
