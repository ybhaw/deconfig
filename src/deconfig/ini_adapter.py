"""
Adapter for getting field value from INI files.

Example Usage:
```python
IniAdapter.set_default_ini_files(["/path/to/common.ini"])

@config([IniAdapter("section1", file_paths=["/path/to/config.ini"])])
class ExampleConfig:
    @field(name="foo")
    def get_foo(self) -> str:
        # Will look for "foo" in "section1"
        # of ["/path/to/common.ini", "/path/to/config.ini"]
        return "default"
```
"""

import configparser
import logging
from dataclasses import dataclass
from typing import Optional, List, Callable, Any, TypeVar

from deconfig.core import AdapterBase, FieldUtil, AdapterError


T = TypeVar("T")
logger = logging.getLogger(__name__)


@dataclass
class _IniAdapterConfig:
    option_name: Optional[str] = None
    section_name: Optional[str] = None
    file_paths: Optional[List[str]] = None
    override_files: bool = True


class IniAdapter(AdapterBase):
    """
    Adapter for getting field value from INI files.

    Parameters:
        section_name: Name of the section in INI file.
        file_names: List of INI file paths.
        override_files: If True, will ignore default INI files.

    Example Usage:
    ```python
    @config([IniAdapter("section1", file_paths=["/path/to/config.ini"])])
    class ExampleConfig:
        @field(name="foo")
        def get_foo(self) -> str:
            return "default" # Will look for "foo" in "section1" of "/path/to/config.ini"
    ```
    """

    _ini_adapter_default_paths: Optional[List[str]] = None

    @staticmethod
    def configure(
        *,
        option_name: Optional[str] = None,
        section_name: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        override_files: bool = False,
    ):
        """
        Decorator for customizing how field is loaded from INI configs.

        Parameters:
            option_name: Name of the option in INI file.
            section_name: Name of the section in INI file.
            file_paths: List of INI file paths.
            override_files: If True, only specified files will be used.

        Example Usage:
        ```python
        @config([IniAdapter("section1", file_paths=["/path/to/config.ini"])])
        class ExampleConfig:
            @IniAdapter.configure(
                option_name="foo", # Will use foo as option even thou field name is bar
                section_name="foo_bar",  # Will use foo_bar as section name
                file_paths=["/path/to/config2.ini"], # Will use this file instead of the config.ini
                override_files=True # Will only use this file
            )
            @field(name="bar")
            def get_bar(self) -> str:
                return "default"
        ```
        """

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
        """
        Set default INI files for all IniAdapter instances.
        This is useful when there are multiple configurations
        referring same INI files.

        Parameters:
            file_paths: List of INI file paths.

        Example Usage:
        ```python
        IniAdapter.set_default_ini_files(["/path/to/config1.ini", "/path/to/config2.ini"])

        @config([IniAdapter(section_name="section1")]) # This will use the defaults
        ...
        ```
        """
        cls._ini_adapter_default_paths = file_paths

    def __init__(
        self,
        section_name: str,
        file_names: Optional[List[str]] = None,
        override_files: bool = False,
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

    def get_field(
        self, field_name: str, method: Callable[..., T], *method_args, **method_kwargs
    ) -> Any:
        section_name = self.section_name
        option_name = field_name

        adapter_configs = FieldUtil.get_adapter_configs(method)
        ini_config: _IniAdapterConfig = adapter_configs.get(IniAdapter)
        if ini_config is not None:
            section_name = ini_config.section_name or section_name
            option_name = ini_config.option_name or option_name
            file_paths = self._get_file_names(
                ini_config.file_paths, ini_config.override_files
            )
        else:
            file_paths = self._get_file_names()

        configparser_ = configparser.ConfigParser()
        configparser_.read(file_paths)

        if section_name is None:
            raise ValueError("No section name specified for IniAdapter")

        try:
            return configparser_.get(section_name, option_name)
        except configparser.NoOptionError as e:
            raise AdapterError(
                f"Field {option_name} not found in {section_name} section of {file_paths}"
            ) from e
