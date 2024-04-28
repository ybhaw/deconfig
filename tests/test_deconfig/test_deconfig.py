"""
Unit tests for `deconfig` module
"""

from unittest.mock import MagicMock

import pytest

from deconfig.core import AdapterBase, AdapterError
# noinspection PyProtectedMember
from deconfig import (
    decorated_config_decorator,
    config, field, optional,
    validate, add_adapter, set_default_adapters,
    EnvAdapter
)
import deconfig


@pytest.mark.parametrize(
    "import_name",
    [
        "field", "optional", "validate", "add_adapter",
        "set_default_adapters", "config", "transform",
        "EnvAdapter", "IniAdapter"
    ],
    ids=[
        "field", "optional", "validate", "add_adapter",
        "set_default_adapters", "config", "transform",
        "EnvAdapter", "IniAdapter"
    ]
)
def test_Should_have_expected_field_When_deconfig_is_imported(import_name):
    assert hasattr(deconfig, import_name)


@pytest.fixture(name="stub_callable")
def fixture_stub_callable():
    def stub_callable():
        """Stub callable"""

    return stub_callable


class TestField:
    def test_Should_raise_type_error_When_name_is_none(self):
        with pytest.raises(TypeError) as e:
            field(None)(lambda: None)
        assert str(e.value) == "Name is required."

    def test_Should_raise_type_error_When_argument_is_not_string(self):
        class StubNotString:
            def __str__(self):
                raise TypeError("Not a string")

        with pytest.raises(TypeError):
            field(StubNotString())(lambda: None)

    def test_Should_set_attribute_name_When_field_is_called(self, stub_callable):
        test_field_decorated = field("test")(stub_callable)

        assert test_field_decorated == stub_callable
        assert hasattr(stub_callable, "name")
        assert stub_callable.name == "test"

    def test_Should_set_attribute_adapter_configs_When_field_is_called(self):
        mock_field = MagicMock()
        response = deconfig.field("test")(mock_field)
        assert hasattr(response, "adapter_configs")

    def test_Should_return_same_function_When_field_is_called(self):
        mock = MagicMock()
        response_callback = field("test")(mock)
        assert response_callback == mock


class TestOptional:
    def test_Should_set_attribute_optional_When_optional_is_called(self, stub_callable):
        response = optional()(stub_callable)
        assert hasattr(response, "optional")
        assert response.optional is True
        assert response == stub_callable

    def test_Should_return_same_function_When_optional_is_called(self):
        mock = MagicMock()
        response_callback = optional()(mock)
        assert response_callback == mock

    def test_Should_set_attribute_optional_to_true_When_optional_is_called_with_true(self):
        test_optional = optional(True)(lambda: None)
        assert hasattr(test_optional, "optional")
        assert test_optional.optional is True

    def test_Should_set_attribute_optional_to_false_When_optional_is_called_with_false(self):
        test_optional = optional(False)(lambda: None)
        assert hasattr(test_optional, "optional")
        assert test_optional.optional is False

    def test_Should_not_raise_type_error_When_argument_cannot_be_cast_to_bool(self):
        class StubNotBool:
            def __bool__(self):
                raise TypeError("Not a bool")

        with pytest.raises(TypeError):
            optional(StubNotBool())(lambda: None)


class TestValidationCallback:

    def test_Should_set_attribute_validation_callback_When_validate_is_called(self, stub_callable):
        test_validation = validate(stub_callable)(lambda: None)
        assert hasattr(test_validation, "validation_callback")
        assert test_validation.validation_callback == stub_callable

    def test_Should_return_same_function_When_validate_is_called(self):
        mock = MagicMock()
        response_callback = validate(mock)(mock)
        assert response_callback == mock

    def test_Should_raise_type_error_When_argument_is_none(self):
        with pytest.raises(TypeError):
            validate(None)(lambda: None)

    def test_Should_raise_type_error_When_argument_is_not_callable(self):
        with pytest.raises(TypeError):
            validate(1)(lambda: None)


class TestAddAdapter:
    def test_Should_set_attribute_adapters_When_add_adapter_is_called(self):
        mock_adapter = MagicMock(AdapterBase)
        get_field_with_added_adapter = add_adapter(mock_adapter())(lambda: None)
        assert hasattr(get_field_with_added_adapter, "adapters")
        assert get_field_with_added_adapter.adapters == [mock_adapter.return_value]

    def test_Should_return_same_function_When_add_adapter_is_called(self):
        mock = MagicMock(AdapterBase)
        response_callback = add_adapter(mock)(mock)
        assert response_callback == mock

    def test_Should_add_adapter_to_existing_adapters_When_add_adapter_is_called(self):
        adapter_1 = MagicMock(AdapterBase)
        field_mock = MagicMock()
        field_mock.adapters = [adapter_1.return_value]

        adapter_2 = MagicMock(AdapterBase)
        field_mock_with_decorator = add_adapter(adapter_2())(field_mock)
        assert hasattr(field_mock_with_decorator, "adapters")
        assert field_mock_with_decorator.adapters == [
            adapter_2.return_value, adapter_1.return_value
        ]

        adapter_3 = MagicMock(AdapterBase)
        field_mock_with_third_adapter = add_adapter(adapter_3())(
            field_mock_with_decorator
        )
        assert hasattr(field_mock_with_third_adapter, "adapters")
        assert field_mock_with_third_adapter.adapters == [
            adapter_3.return_value,
            adapter_2.return_value,
            adapter_1.return_value
        ]

    def test_Should_add_adapter_as_new_list_When_add_adapter_is_called(
            self, stub_callable
    ):
        mock_adapter = MagicMock(AdapterBase)
        assert not hasattr(stub_callable, "adapters")
        field_decorated = add_adapter(mock_adapter())(stub_callable)
        assert hasattr(field_decorated, "adapters")
        assert field_decorated.adapters == [mock_adapter.return_value]

    def test_Should_raise_value_error_When_argument_is_none(self):
        with pytest.raises(TypeError):
            add_adapter(None)(lambda: None)

    def test_Should_raise_value_error_When_argument_is_not_adapter_base(self):
        with pytest.raises(TypeError):
            add_adapter(1)(lambda: None)


class TestSetDefaultAdapters:
    def test_Should_set_default_adapters_to_env_adapter_When_set_default_adapters_is_not_called(self):
        _adapters = deconfig._adapters  # pylint: disable=protected-access
        assert len(_adapters) == 1
        assert isinstance(_adapters[0], EnvAdapter)
        mocked_adapter = MagicMock(AdapterBase)
        config_response = MagicMock("config_response")
        mocked_adapter.get_field.return_value = config_response
        _adapters.insert(0, mocked_adapter)

        @config()
        class StubConfig:
            @field(name="test")
            def stub_field(self):
                """Stub field"""

        test_config = StubConfig()
        assert test_config.stub_field() == config_response

    def test_Should_raise_type_error_When_set_default_adapters_is_called_with_no_adapters(self):
        with pytest.raises(TypeError):
            set_default_adapters()

    def test_Should_raise_type_error_When_set_default_adapters_is_called_with_non_adapter_base(self):
        with pytest.raises(TypeError):
            set_default_adapters(1)
        with pytest.raises(TypeError):
            set_default_adapters(EnvAdapter(), 1)

    def test_Should_set_default_adapters_to_given_adapters_When_set_default_adapters_is_called_with_adapters(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        set_default_adapters(adapter)

        @config()
        class StubConfig:
            @field(name="field")
            def test_field(self):
                """Stub field"""

        stub_config = StubConfig()
        assert stub_config.test_field() == adapter_response


class TestConfig:
    def test_Should_use_env_adapter_When_no_adapters_are_set(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response
        deconfig._adapters = [adapter]  # pylint: disable=protected-access

        @config()
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == adapter_response

    def test_Should_update_and_use_class_adapters_When_adapters_set_using_decorator_args(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config([adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == adapter_response

    def test_Should_update_and_use_class_adapters_When_adapters_set_using_set_default_adapters(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        set_default_adapters(adapter)

        @config()
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == adapter_response

    def test_Should_prioritize_config_args_When_config_has_adapters_and_default_is_also_set(self):
        default_adapter = MagicMock(AdapterBase)

        arg_adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        arg_adapter.get_field.return_value = adapter_response

        set_default_adapters(default_adapter)

        @config([arg_adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == adapter_response

    def test_Should_only_configure_methods_with_field_decorator_When_config_is_called(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config(adapters=[adapter])
        class StubConfig:
            # noinspection PyMethodMayBeStatic
            def stub_method_without_field_decorator(self):
                """Method without field decorator"""
                return 1

            @field(name="test")
            def stub_method_with_field_decorator(self):
                """Field with adapter"""

        stub_config = StubConfig()
        assert stub_config.stub_method_with_field_decorator() == adapter_response
        assert stub_config.stub_method_without_field_decorator() == 1
        assert adapter.get_field.call_count == 1

    def test_Should_prioritize_methods_adapters_When_method_has_adapters(self):
        method_adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        method_adapter.get_field.return_value = adapter_response

        class_adapter = MagicMock(AdapterBase)
        default_adapter_response = MagicMock("default_adapter_response")
        class_adapter.get_field.return_value = default_adapter_response

        @config(adapters=[class_adapter])
        class StubConfig:
            @add_adapter(method_adapter)
            @field(name="test")
            def method_with_field_adapter(self):
                """Field with adapter"""

            @field(name="test_2")
            def method_without_field_decorator(self):
                """Field without adapter"""

        stub_config = StubConfig()
        assert stub_config.method_with_field_adapter() == adapter_response
        assert stub_config.method_without_field_decorator() == default_adapter_response
        assert method_adapter.get_field.call_count == 1
        assert class_adapter.get_field.call_count == 1

    def test_Should_use_class_adapters_When_field_missing_in_field_adapters(self):
        method_adapter = MagicMock(AdapterBase)
        method_adapter.get_field.side_effect = AdapterError("Intentional error")

        class_adapter = MagicMock(AdapterBase)
        default_adapter_response = MagicMock("default_adapter_response")
        class_adapter.get_field.return_value = default_adapter_response

        @config(adapters=[class_adapter])
        class StubConfig:
            @add_adapter(method_adapter)
            @field(name="test")
            def method_with_field_adapter(self):
                """Field with adapter"""

            @field(name="test_2")
            def method_without_field_decorator(self):
                """Field without adapter"""

        stub_config = StubConfig()
        assert stub_config.method_with_field_adapter() == default_adapter_response
        assert method_adapter.get_field.call_count == 1
        assert class_adapter.get_field.call_count == 1

    def test_Should_update_field_methods_with_decorated_config_decorator_When_class_is_decorated_with_config(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config([adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        assert stub_config.field_stub() == adapter_response
        assert stub_config.field_stub.__name__ == "decorated_config_wrapper"

    def test_Should_add_reset_deconfig_cache_method_When_class_is_decorated_with_config(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config([adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

        stub_config = StubConfig()
        stub_config.field_stub()
        assert hasattr(stub_config, "reset_deconfig_cache")
        assert callable(stub_config.reset_deconfig_cache)
        stub_config.reset_deconfig_cache()

    def test_Should_not_create_reset_deconfig_cache_When_class_already_has_reset_deconfig_cache_method(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        config_cache_stub = MagicMock()

        @config([adapter])
        class StubConfig:
            @field(name="test")
            def field_stub(self):
                """Stub Field"""

            def reset_deconfig_cache(self):
                """Method already present"""
                return config_cache_stub

        stub_config = StubConfig()
        assert hasattr(stub_config, "reset_deconfig_cache")
        assert stub_config.reset_deconfig_cache() == config_cache_stub


class TestDecoratedConfigDecorator:
    def test_Should_raise_value_error_When_field_name_is_not_present(self, stub_callable):
        with pytest.raises(ValueError) as e:
            decorated_config_decorator(stub_callable)
        assert str(e.value) == "Have you forgotten to decorate field with @field(name='name')?"

    def test_Should_raise_value_error_When_adapters_are_not_present(self, stub_callable):
        stub_callable.name = "test"
        with pytest.raises(ValueError) as e:
            decorated_config_decorator(stub_callable)
        assert str(e.value) == "Class not decorated with @config"

    def test_Should_mandate_field_be_present_in_config_false_When_optional_is_not_set_or_is_false(self):
        adapter = MagicMock()
        adapter.get_field.side_effect = AdapterError("Value not found")

        def stub_callable_without_optional():
            """Stub callable without optional"""

        stub_callable_without_optional.name = "test"
        stub_callable_without_optional.adapters = [adapter]
        response_callback = decorated_config_decorator(stub_callable_without_optional)
        with pytest.raises(ValueError) as e:
            response_callback()
        assert str(e.value) == "Field test not found in any config."

        def stub_callable_with_optional_false():
            """Stub callable with optional false"""

        stub_callable_with_optional_false.name = "test_2"
        stub_callable_with_optional_false.adapters = [adapter]
        stub_callable_with_optional_false.optional = False
        response_callback = decorated_config_decorator(stub_callable_with_optional_false)
        with pytest.raises(ValueError) as e:
            response_callback()
        assert str(e.value) == "Field test_2 not found in any config."

    def test_Should_set_optional_to_true_When_optional_is_set_to_true(self, stub_callable):
        adapter = MagicMock()
        adapter.get_field.side_effect = AdapterError("Value not found")

        stub_callable.name = "test"
        stub_callable.adapters = [adapter]
        stub_callable.optional = True
        response = decorated_config_decorator(stub_callable)
        assert response() is None

    def test_Should_call_validation_callback_When_set(self, stub_callable):
        adapter = MagicMock()
        adapter.get_field.return_value = 1

        validation_callback = MagicMock()
        stub_callable.name = "test"
        stub_callable.adapters = [adapter]
        stub_callable.validation_callback = validation_callback
        response = decorated_config_decorator(stub_callable)
        response()
        validation_callback.assert_called_once_with(1)

    def test_Should_raise_value_error_When_validation_callback_raises_error(self, stub_callable):
        adapter = MagicMock()
        validation_callback = MagicMock()
        validation_callback.side_effect = ValueError("Validation error")
        stub_callable.name = "test"
        stub_callable.adapters = [adapter]
        stub_callable.validation_callback = validation_callback
        response = decorated_config_decorator(stub_callable)
        with pytest.raises(ValueError) as e:
            response()
        validation_callback.assert_called_once_with(adapter.get_field.return_value)
        assert str(e.value) == "Validation error"

    def test_Should_call_transform_callback_When_set(self, stub_callable):
        adapter = MagicMock()
        adapter.get_field.return_value = 1

        transform_callback = MagicMock()
        transform_callback.return_value = 2
        stub_callable.name = "test"
        stub_callable.adapters = [adapter]
        stub_callable.transform_callback = transform_callback
        response = decorated_config_decorator(stub_callable)
        assert response() == 2
        transform_callback.assert_called_once_with(1)

    def test_Should_cache_transformed_response_When_invoked_and_has_transformer(self, stub_callable):
        adapter = MagicMock()
        adapter.get_field.side_effect = [1]
        stub_callable.name = "test"
        stub_callable.adapters = [adapter]
        transform_callback = MagicMock()
        stub_callable.transform_callback = transform_callback
        response = decorated_config_decorator(stub_callable)
        assert response() == transform_callback.return_value
        assert response() == transform_callback.return_value
        assert transform_callback.call_count == 1

    def test_Should_cache_response_When_invoked(self, stub_callable):
        adapter = MagicMock()
        adapter.get_field.side_effect = [1]
        stub_callable.name = "test"
        stub_callable.adapters = [adapter]
        response = decorated_config_decorator(stub_callable)
        assert response() == 1
        assert response() == 1
        assert adapter.get_field.call_count == 1

    def test_Should_rebuild_value_When_cache_reset_using_reset_deconfig_cache(self):
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
        stub_config.reset_deconfig_cache()
        assert stub_config.stub_field() == 1
        assert stub_config.stub_field() == 1
        assert adapter.get_field.call_count == 2
        stub_config.reset_deconfig_cache()
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
        response = decorated_config_decorator(stub_callable)
        response()
        assert adapter_1.get_field.call_count == 1
        assert adapter_2.get_field.call_count == 1
        assert adapter_3.get_field.call_count == 0
