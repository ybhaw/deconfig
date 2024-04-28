"""
Derives configuration value from environment variables.
Uses field name in uppercase as environment variable name by default.
You can specify environment variable name with `@EnvAdapter.configure` decorator.

Example Usage:
```python
@config([EnvAdapter(env_prefix="MYAPP_")])
class ExampleConfig:
    @field(name="foo")
    def get_foo(self) -> str:
        return "default" # Returns value of "MYAPP_FOO" environment variable

    @EnvAdapter.configure(override_name="bar", ignore_prefix=True)
    @field(name="bar")
    def get_bar(self) -> str:
        return "default" # Returns value of "bar" environment variable
```
"""


import os
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

from deconfig.core import AdapterBase, FieldUtil, AdapterError


T = TypeVar("T")


@dataclass
class _EnvAdapterConfig:
    override_name: Optional[str] = None
    ignore_prefix: bool = False


class EnvAdapter(AdapterBase):
    """
    Adapter for getting field value from environment variables.
    You can specify environment variable name with @EnvAdapter.configure decorator,
    or use field name in uppercase as environment variable name.

    :param env_prefix: Prefix for environment variable names.
    """

    @staticmethod
    def configure(override_name: Optional[str] = None, ignore_prefix: bool = False):
        """
        Decorator for setting environment variable name.

        :param override_name: Environment variable name.
        :param ignore_prefix: Override prefix for environment variable name.
        """

        def wrapper(func):
            env_config: _EnvAdapterConfig = FieldUtil.get_adapter_configs(func).get(
                EnvAdapter, _EnvAdapterConfig()
            )
            env_config.override_name = override_name
            env_config.ignore_prefix = ignore_prefix
            FieldUtil.upsert_adapter_config(func, EnvAdapter, env_config)
            return func

        return wrapper

    def __init__(self, env_prefix: str = ""):
        self._env_prefix = env_prefix

    # pylint: disable=unused-argument
    def get_field(self, field_name: str, method: Callable[..., T], *args, **kwargs) -> str:
        env_config: Optional[_EnvAdapterConfig] = (
            FieldUtil.get_adapter_configs(method).get(EnvAdapter)
        )

        env_name = field_name.upper()
        if env_config and env_config.override_name is not None:
            env_name = env_config.override_name

        prefix = self._env_prefix
        if env_config and env_config.ignore_prefix:
            prefix = ""

        env_name = prefix + env_name
        if env_name not in os.environ:
            raise AdapterError(f"Environment variable {env_name} not found.")
        return os.environ[env_name]
