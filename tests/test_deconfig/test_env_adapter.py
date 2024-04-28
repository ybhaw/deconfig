import os
from typing import Dict, Any

import pytest

from deconfig import field
from deconfig.core import AdapterError


class TestEnvAdapter:
    default_env_variables: Dict[str, Any] = {}

    @pytest.fixture(scope="module", autouse=True)
    def setup_class(self):
        for key, value in os.environ.items():
            self.default_env_variables[key] = value

    def setup_method(self):
        for key in os.environ.keys():
            if key not in self.default_env_variables:
                del os.environ[key]
                continue
            os.environ[key] = self.default_env_variables[key]

    def test_Should_be_extending_AdapterBase(self):
        from deconfig.env_adapter import EnvAdapter
        from deconfig.core import AdapterBase
        assert issubclass(EnvAdapter, AdapterBase)

    def test_Should_be_importable_from_deconfig_and_env_adapter_modules(self):
        from deconfig import EnvAdapter
        _ = EnvAdapter()
        from deconfig.env_adapter import EnvAdapter
        _ = EnvAdapter()

    def test_Should_not_add_a_prefix_When_default_env_adapter_is_used(self):
        from deconfig.env_adapter import EnvAdapter
        import os
        adapter = EnvAdapter()
        os.environ["STUB"] = "stub_value"

        field_callback = field(name="stub")(lambda: None)
        assert adapter.get_field("stub", field_callback) == "stub_value"

    def test_Should_add_a_prefix_When_prefix_is_set(self):
        from deconfig.env_adapter import EnvAdapter
        import os
        prefix = "STUB_"
        field_name = "Stub"

        adapter = EnvAdapter(env_prefix=prefix)
        os.environ[prefix + field_name.upper()] = "stub_stub_value"
        field_callback = field(name=field_name)(lambda: None)
        assert adapter.get_field(field_name, field_callback) == "stub_stub_value"

    def test_Should_uppercase_field_name_When_no_override_is_provided(self):
        from deconfig.env_adapter import EnvAdapter
        import os
        field_name = "Stub"
        adapter = EnvAdapter()
        os.environ[field_name.upper()] = "stub_value"
        field_callback = field(name=field_name)(lambda: None)
        assert adapter.get_field(field_name, field_callback) == "stub_value"

    def test_Should_not_uppercase_prefix_When_prefix_is_provided(self):
        from deconfig.env_adapter import EnvAdapter
        import os
        prefix = "STuB_"
        field_name = "Stub"
        expected_env_key = prefix + field_name.upper()
        os.environ[expected_env_key] = "stub_value"
        adapter = EnvAdapter(env_prefix=prefix)
        field_callback = field(name=field_name)(lambda: None)
        assert adapter.get_field(field_name, field_callback) == "stub_value"

    def test_Should_use_override_name_When_override_name_is_provided_in_config(self):
        from deconfig.env_adapter import EnvAdapter
        import os
        prefix = "STUB_"
        field_name = "Stub"
        override_name = "Stub_Override"

        adapter = EnvAdapter(prefix)
        os.environ[prefix + override_name] = "stub_value"

        field_callback = EnvAdapter.configure(override_name=override_name)(field(name=field_name)(lambda : None))
        assert adapter.get_field(field_name, field_callback) == "stub_value"

    def test_Should_not_uppercase_overridden_name_When_provided(self):
        from deconfig.env_adapter import EnvAdapter
        import os
        prefix = "STUB_"
        field_name = "Stub"
        override_name = "Stub_Override"

        adapter = EnvAdapter(prefix)
        os.environ[prefix + override_name] = "stub_value"
        field_callback = EnvAdapter.configure(override_name=override_name)(field(name=field_name)(lambda: None))

        assert adapter.get_field(field_name, field_callback) == "stub_value"

    def test_Should_ignore_prefix_When_ignore_prefix_is_set(self):
        from deconfig.env_adapter import EnvAdapter
        import os
        prefix = "STUB_"
        field_name = "Stub"
        os.environ[field_name.upper()] = "stub_value"

        adapter = EnvAdapter(prefix)
        field_callback = EnvAdapter.configure(ignore_prefix=True)(field(field_name)(lambda: None))
        assert adapter.get_field(field_name, field_callback) == "stub_value"

    def test_Should_raise_attribute_error_When_env_variable_is_not_set(self):
        from deconfig.env_adapter import EnvAdapter
        adapter = EnvAdapter()
        field_callback = field("stub")(lambda: None)
        with pytest.raises(AdapterError):
            adapter.get_field("STUB", field_callback)

    def test_Should_raise_value_error_When_get_field_is_called_on_normal_method(self):
        from deconfig.env_adapter import EnvAdapter
        adapter = EnvAdapter()
        with pytest.raises(ValueError):
            adapter.get_field("STUB", lambda: None)
