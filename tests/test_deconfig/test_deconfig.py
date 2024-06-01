"""
Unit tests for `deconfig` module
"""

from unittest.mock import MagicMock

import pytest

import deconfig

# noinspection PyProtectedMember
from deconfig import (
    _decorated_config_decorator,
    config,
    field,
    optional,
    add_adapter,
    set_default_adapters,
    EnvAdapter,
)
from deconfig.core import AdapterBase, AdapterError, FieldUtil


@pytest.mark.parametrize(
    "import_name",
    [
        "field",
        "optional",
        "add_adapter",
        "set_default_adapters",
        "config",
        "EnvAdapter",
        "IniAdapter",
    ],
    ids=[
        "field",
        "optional",
        "add_adapter",
        "set_default_adapters",
        "config",
        "EnvAdapter",
        "IniAdapter",
    ],
)
def test_Should_have_expected_field_When_deconfig_is_imported(import_name):
    assert hasattr(deconfig, import_name)


@pytest.fixture(name="stub_callable")
def fixture_stub_callable():
    def stub_callable():
        """Stub callable"""

    return stub_callable


# noinspection PyArgumentList,PyTypeChecker
class TestField:
    # pylint: disable=no-value-for-parameter
    def test_Should_raise_type_error_When_name_is_none_or_missing(self):
        with pytest.raises(TypeError) as e:
            field()(lambda: None)
        assert str(e.value) == "field() missing 1 required positional argument: 'name'"

        with pytest.raises(TypeError) as e:
            field(None)(lambda: None)

        assert str(e.value) == "Name is required."

    def test_Should_raise_type_error_When_argument_is_not_string(self):
        class StubNotString:
            def __str__(self):
                raise TypeError("Not a string")

        with pytest.raises(TypeError):
            field(StubNotString())(lambda: None)

    def test_Should_set_attribute_name_When_field_is_called(self):
        field_name = "stub_field_name"

        @field(field_name)
        def stub_field():
            """Pass"""

        assert FieldUtil.has_name(stub_field) is True
        assert FieldUtil.get_name(stub_field) == field_name

    def test_Should_set_attribute_adapter_configs_When_field_is_called(self):
        def stub_method():
            """Stub method"""

        decorated_method = field("test")(stub_method)
        assert FieldUtil.get_adapter_configs(decorated_method) == {}

    def test_Should_return_same_function_When_field_is_called(self):
        mock = MagicMock()
        response_callback = field("test")(mock)
        assert response_callback == mock


# noinspection PyTypeChecker
class TestOptional:
    def test_Should_return_same_function_When_optional_is_called(self):
        mock = MagicMock()
        response_callback = optional()(mock)
        assert response_callback == mock

    def test_Should_return_false_When_optional_is_not_set(self):
        @field(name="stub_function")
        def stub_function():
            """Stub function"""

        assert FieldUtil.is_optional(stub_function) is False

    def test_Should_set_true_When_optional_is_called_without_arguments(self):
        @optional()
        @field(name="stub_field")
        def stub_field():
            """Stub field"""

        assert FieldUtil.is_optional(stub_field) is True

    def test_Should_set_attribute_optional_to_true_When_optional_is_called_with_true(
        self,
    ):
        @optional(True)
        @field(name="stub_field")
        def stub_field():
            """Stub field"""

        assert FieldUtil.is_optional(stub_field) is True

    def test_Should_be_false_When_optional_is_called_with_false(
        self,
    ):
        @optional(False)
        @field(name="stub_field")
        def stub_field():
            """Stub field"""

        assert FieldUtil.is_optional(stub_field) is False

    def test_Should_not_raise_type_error_When_argument_cannot_be_cast_to_bool(self):
        class StubNotBool:
            def __bool__(self):
                raise TypeError("Not a bool")

        with pytest.raises(TypeError):
            optional(StubNotBool())(field(name="stub_field")(lambda: None))


@pytest.fixture(name="stub_adapter")
def fixture_stub_adapter():
    class StubAdapter(AdapterBase):
        def get_field(self, field_name, method, *_, **__):
            return "stub_adapter_response"

    return StubAdapter()


# noinspection PyTypeChecker
class TestAddAdapter:

    def test_Should_set_attribute_adapters_When_add_adapter_is_called(
        self, stub_adapter
    ):
        @add_adapter(stub_adapter)
        @field(name="test")
        def stub_field():
            """Stub field"""

        assert FieldUtil.get_adapters(stub_field) == [stub_adapter]

    def test_Should_return_same_function_When_add_adapter_is_called(self, stub_adapter):
        @field(name="test")
        def stub_field():
            """Stub Field"""

        assert stub_field == add_adapter(stub_adapter)(stub_field)

    def test_Should_add_adapter_to_existing_adapters_When_add_adapter_is_called(self):
        class StubAdapter1(AdapterBase):
            def get_field(self, field_name, method, *_, **__):
                return "stub_adapter_response_1"

        class StubAdapter2(AdapterBase):
            called_once = False
            error_raised = False

            def get_field(self, field_name, method, *_, **__):
                if not self.called_once:
                    self.called_once = True
                    return "stub_adapter_response_2"
                raise AdapterError("Intentional error")

        stub_adapter_2 = StubAdapter2()

        @config()
        class StubConfig:
            @add_adapter(stub_adapter_2)
            @add_adapter(StubAdapter1())
            @field(name="test")
            def stub_field(self):
                """Stub field"""

        stub_config = StubConfig()
        assert stub_config.stub_field() == "stub_adapter_response_2"
        deconfig.reset_cache(stub_config)
        assert stub_config.stub_field() == "stub_adapter_response_1"
        with pytest.raises(AdapterError):
            stub_adapter_2.get_field("test", stub_config.stub_field)

    def test_Should_add_adapter_as_new_list_When_add_adapter_is_called(
        self, stub_callable, stub_adapter
    ):
        assert not FieldUtil.has_adapters(stub_callable)
        field_decorated = add_adapter(stub_adapter)(stub_callable)
        assert FieldUtil.has_adapters(field_decorated)
        assert FieldUtil.get_adapters(field_decorated) == [stub_adapter]

    def test_Should_raise_value_error_When_argument_is_none(self):
        with pytest.raises(TypeError) as e:
            add_adapter(None)(field(name="test")(lambda: None))

        assert str(e.value) == "Adapter is required."

    def test_Should_raise_value_error_When_argument_is_not_adapter_base(self):
        with pytest.raises(TypeError) as e:
            add_adapter(1)(field(name="test")(lambda: None))

        assert (
            str(e.value) == "Adapter must extend AdapterBase or have get_field method."
        )


# noinspection PyTypeChecker
class TestSetDefaultAdapters:
    def test_Should_set_default_adapters_to_env_adapter_When_set_default_adapters_is_not_called(
        self, monkeypatch
    ):
        monkeypatch.setenv("STUB_FIELD", "stub_response")

        @config()
        class StubConfig:
            @field(name="stub_field")
            def stub_field(self):
                """Stub field"""

        stub_config = StubConfig()
        assert stub_config.stub_field() == "stub_response"

    def test_Should_raise_type_error_When_set_default_adapters_is_called_with_no_adapters(
        self,
    ):
        with pytest.raises(TypeError) as e:
            set_default_adapters()

        assert str(e.value) == "At least one adapter is required."

    def test_Should_raise_type_error_When_set_default_adapters_is_called_with_non_adapter_base(
        self,
    ):
        with pytest.raises(TypeError) as e:
            set_default_adapters(1)

        assert (
            str(e.value) == "Adapter must extend AdapterBase or have get_field method."
        )

        with pytest.raises(TypeError) as e:
            set_default_adapters(EnvAdapter(), 1)

        assert (
            str(e.value) == "Adapter must extend AdapterBase or have get_field method."
        )

    def test_Should_set_default_adapters_to_given_adapters_When_set_default_adapters_is_called_with_adapters(
        self, stub_adapter, monkeypatch
    ):
        monkeypatch.setenv("STUB_ENV_FIELD", "stub_env_response")
        set_default_adapters(stub_adapter)

        @config()
        class StubConfig:
            @field(name="default_adapter")
            def default_stub_field(self):
                """Stub field"""

            @add_adapter(EnvAdapter())
            @field(name="stub_env_field")
            def stub_env_field(self):
                """Stub field"""

        stub_config = StubConfig()
        assert stub_config.stub_env_field() == "stub_env_response"
        assert stub_config.default_stub_field() == "stub_adapter_response"


class TestConfig:

    def test_Should_use_env_adapter_When_no_adapters_are_set(self, monkeypatch):
        monkeypatch.setenv("STUB_ENV_FIELD", "stub_env_response")
        set_default_adapters(EnvAdapter())

        @config()
        class StubConfig:
            @field(name="stub_env_field")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == "stub_env_response"

    def test_Should_update_and_use_class_adapters_When_adapters_set_using_decorator_args(
        self, stub_adapter
    ):
        @config([stub_adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == "stub_adapter_response"

    def test_Should_update_and_use_default_adapters_When_adapters_set_using_set_default_adapters(
        self, stub_adapter
    ):
        set_default_adapters(stub_adapter)

        @config()
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == "stub_adapter_response"

    def test_Should_prioritize_config_args_When_config_has_adapters_and_default_is_also_set(
        self, stub_adapter
    ):
        class StubAdapter2(AdapterBase):
            def get_field(self, field_name, method, *_, **__):
                return "stub_adapter_response_2"

        set_default_adapters(stub_adapter)

        @config([StubAdapter2()])
        class StubConfig:

            @add_adapter(StubAdapter2())
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == "stub_adapter_response_2"

    def test_Should_only_configure_methods_with_field_decorator_When_config_is_called(
        self, stub_adapter
    ):
        @config(adapters=[stub_adapter])
        class StubConfig:
            # noinspection PyMethodMayBeStatic
            def stub_method_without_field_decorator(self):
                """Method without field decorator"""
                return 1

            @field(name="test")
            def stub_method_with_field_decorator(self):
                """Field with adapter"""

        stub_config = StubConfig()
        assert stub_config.stub_method_with_field_decorator() == "stub_adapter_response"
        assert stub_config.stub_method_without_field_decorator() == 1

    def test_Should_prioritize_methods_adapters_When_method_has_adapters(self):
        class StubAdapter1(AdapterBase):
            def get_field(self, field_name, method, *_, **__):
                if field_name == "no_has_no_value":
                    raise AdapterError("Intentional error")
                return "stub_adapter_response_1"

        class StubAdapter2(AdapterBase):
            def get_field(self, field_name, method, *_, **__):
                if field_name == "no_has_no_value":
                    raise AdapterError("Intentional error")
                return "stub_adapter_response_2"

        @config(adapters=[StubAdapter1()])
        class StubConfig:
            @add_adapter(StubAdapter2())
            @field(name="test")
            def method_with_field_adapter(self):
                """Field with adapter"""

            @field(name="test_2")
            def method_without_field_decorator(self):
                """Field without adapter"""

            @add_adapter(StubAdapter2())
            @field(name="no_has_no_value")
            def method_with_no_value(self):
                """Field with adapter"""

        stub_config = StubConfig()
        assert stub_config.method_with_field_adapter() == "stub_adapter_response_2"
        assert stub_config.method_without_field_decorator() == "stub_adapter_response_1"
        with pytest.raises(ValueError):
            stub_config.method_with_no_value()

    def test_Should_use_class_adapters_When_field_missing_in_field_adapters(
        self, stub_adapter
    ):
        class StubAdapter2(AdapterBase):
            def get_field(self, field_name, method, *_, **__):
                if field_name == "field_present_in_adapter_2":
                    return "stub_adapter_response_2"
                raise AdapterError("Intentional error")

        @config(adapters=[stub_adapter])
        class StubConfig:
            @add_adapter(StubAdapter2())
            @field(name="field_present_in_adapter_2")
            def method_with_field_adapter(self):
                """Field with adapter"""

            @add_adapter(StubAdapter2())
            @field(name="field_missing_in_adapter_2")
            def method_without_field_adapter(self):
                """Field with adapter"""

            @field(name="test_2")
            def method_without_field_decorator(self):
                """Field without adapter"""

        stub_config = StubConfig()
        assert stub_config.method_with_field_adapter() == "stub_adapter_response_2"
        assert stub_config.method_without_field_adapter() == "stub_adapter_response"
        assert stub_config.method_without_field_decorator() == "stub_adapter_response"

    def test_Should_have_original_function_When_class_is_decorated_with_config(
        self, stub_adapter
    ):
        @config([stub_adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert FieldUtil.has_original_function(stub_config.field_stub)

    def test_Should_not_create_reset_deconfig_cache_When_class_already_has_reset_deconfig_cache_method(
        self,
    ):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        config_cache_stub = MagicMock()

        @config([adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

            @staticmethod
            def reset_deconfig_cache():
                """Method already present"""
                return config_cache_stub

        stub_config = StubConfig()
        assert stub_config.reset_deconfig_cache() == config_cache_stub


class TestDecoratedConfigDecorator:
    def test_Should_raise_value_error_When_adapters_are_not_present(
        self, stub_callable
    ):
        stub_callable.name = "test"

        class StubConfig:
            @field(name="test")
            def stub_field(self):
                """Stub field"""
                return "config_not_called"

        stub_config = StubConfig()
        assert stub_config.stub_field() == "config_not_called"

    def test_Should_mandate_field_be_present_in_config_false_When_optional_is_not_set_or_is_false(
        self,
    ):
        class StubAdapter2(AdapterBase):
            def get_field(self, field_name, method, *_, **__):
                raise AdapterError("Intentional error")

        @config(adapters=[StubAdapter2()])
        class StubConfig:
            @field(name="test")
            def stub_field(self):
                """Stub field"""

        stub_config = StubConfig()
        with pytest.raises(ValueError) as e:
            stub_config.stub_field()
        assert str(e.value) == "Field test not found in any config."

    def test_Should_set_optional_to_true_When_optional_is_set_to_true(self):
        class StubAdapter2(AdapterBase):
            def get_field(self, field_name, method, *_, **__):
                raise AdapterError("Intentional error")

        @config(adapters=[StubAdapter2()])
        class StubConfig:
            @optional()
            @field(name="test")
            def stub_field(self):
                """Stub field"""

        stub_config = StubConfig()
        assert stub_config.stub_field() is None

    def test_Should_cache_response_When_invoked(self, stub_callable):
        adapter = MagicMock()
        adapter.get_field.side_effect = [1]
        stub_callable.name = "test"
        stub_callable.adapters = [adapter]
        response = _decorated_config_decorator(stub_callable)
        assert response() == 1
        assert response() == 1
        assert adapter.get_field.call_count == 1

    def test_Should_rebuild_value_When_cache_reset_using_reset_cache(self):
        adapter = MagicMock(AdapterBase)
        adapter.get_field.side_effect = [AdapterError, 1, 2]

        @config([adapter])
        class StubConfig:
            @optional()
            @field(name="test")
            def stub_field(self):
                return 0

        stub_config = StubConfig()
        assert stub_config.stub_field() == 0
        assert stub_config.stub_field() == 0
        assert adapter.get_field.call_count == 1
        deconfig.reset_cache(stub_config)
        assert stub_config.stub_field() == 1
        assert stub_config.stub_field() == 1
        assert adapter.get_field.call_count == 2
        deconfig.reset_cache(stub_config)
        assert stub_config.stub_field() == 2
        assert stub_config.stub_field() == 2
        assert adapter.get_field.call_count == 3

    def test_Should_call_adapters_in_sequence_When_invoked(self, stub_callable):
        adapter_1 = MagicMock(AdapterBase)
        adapter_2 = MagicMock(AdapterBase)
        adapter_3 = MagicMock(AdapterBase)
        adapter_1.get_field.side_effect = AdapterError("Value not found")
        adapter_2.get_field.side_effect = [1]
        adapter_3.get_field.side_effect = [None]

        stub_callable.name = "test"
        stub_callable.adapters = [adapter_1, adapter_2, adapter_3]
        response = _decorated_config_decorator(stub_callable)
        response()
        assert adapter_1.get_field.call_count == 1
        assert adapter_2.get_field.call_count == 1
        assert adapter_3.get_field.call_count == 0


class TestResetCache:
    def test_Should_reset_cache_When_reset_cache_is_invoked(self):
        class AdapterStub(AdapterBase):
            """Stub Adapter"""
            is_first_invoke = True

            def get_field(self, field_name, method, *_, **__):
                if self.is_first_invoke:
                    self.is_first_invoke = False
                    return 1
                return 2

        @config([AdapterStub()])
        class StubConfig:
            """Stub Config"""
            @field(name="test")
            def stub_field(self):
                """
                Stub field
                """

        stub_config = StubConfig()
        assert stub_config.stub_field() == 1
        assert stub_config.stub_field() == 1
        deconfig.reset_cache(stub_config)
        assert stub_config.stub_field() == 2

    def test_Should_do_nothing_When_reset_cache_is_invoked_on_non_set_cache(self):
        class AdapterStub(AdapterBase):
            """ Stub adapter """
            is_first_invoke = True

            def get_field(self, field_name, method, *_, **__):
                return 1

        @config([AdapterStub()])
        class StubConfig:
            """ Stub Config """
            @field(name="test")
            def stub_field(self):
                """
                Stub field
                """

        stub_config = StubConfig()
        deconfig.reset_cache(stub_config)
        assert stub_config.stub_field() == 1
