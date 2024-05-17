"""
Unit tests for the `deconfig.core` module
"""

from typing import Type
from unittest.mock import MagicMock

import pytest

from deconfig.core import FieldUtil, AdapterBase, is_callable


@pytest.fixture(name="stub_function")
def fixture_stub_function():
    def stub_function():
        """Stub Function"""

    return stub_function


@pytest.mark.parametrize(
    "callback_arg, expected_error_message",
    [
        (1, "Callback must be a callable."),
        (None, "Callback is required."),
        (lambda: None, None),
    ]
)
def test_is_callable(callback_arg, expected_error_message):
    if expected_error_message:
        with pytest.raises(TypeError) as e:
            is_callable(callback_arg)
        assert str(e.value) == expected_error_message
    else:
        is_callable(callback_arg)


class TestAdapterConfig:
    def test_Should_add_empty_dict_as_adapter_config_attribute_When_initialized(
        self, stub_function
    ):
        FieldUtil.initialize_adapter_configs(stub_function)
        assert hasattr(stub_function, "adapter_configs")
        assert getattr(stub_function, "adapter_configs") == {}

    def test_Should_return_adapter_configs_When_get_adapter_configs_is_called(
        self, stub_function
    ):
        FieldUtil.initialize_adapter_configs(stub_function)
        config = MagicMock()
        FieldUtil.upsert_adapter_config(stub_function, AdapterBase, config)
        assert FieldUtil.get_adapter_configs(stub_function) == {AdapterBase: config}

    def test_Should_raise_error_When_get_adapter_configs_is_called_and_adapter_configs_is_not_set(
        self, stub_function
    ):
        with pytest.raises(ValueError):
            FieldUtil.get_adapter_configs(stub_function)

    # noinspection PyTypeChecker
    def test_Should_add_adapter_config_When_upsert_adapter_config_is_called(
        self, stub_function
    ):
        FieldUtil.initialize_adapter_configs(stub_function)
        adapter_1: Type[AdapterBase] = MagicMock(AdapterBase)
        adapter_config_1 = MagicMock()
        FieldUtil.upsert_adapter_config(stub_function, adapter_1, adapter_config_1)

        assert FieldUtil.get_adapter_configs(stub_function) == {
            adapter_1: adapter_config_1
        }

        adapter_2: Type[AdapterBase] = MagicMock(AdapterBase)
        adapter_config_2 = MagicMock()
        FieldUtil.upsert_adapter_config(stub_function, adapter_2, adapter_config_2)
        assert FieldUtil.get_adapter_configs(stub_function) == {
            adapter_1: adapter_config_1,
            adapter_2: adapter_config_2,
        }


class TestAdapters:
    def test_Should_set_adapters_When_set_adapters_is_called(self, stub_function):
        adapters = [MagicMock()]
        FieldUtil.set_adapters(stub_function, adapters)
        assert getattr(stub_function, "adapters") == adapters

    def test_Should_add_adapter_When_add_adapter_is_called(self, stub_function):
        adapter = MagicMock()
        FieldUtil.add_adapter(stub_function, adapter)
        assert FieldUtil.get_adapters(stub_function) == [adapter]

    def test_Should_return_adapters_When_get_adapters_is_called(self, stub_function):
        stub_adapter = MagicMock(AdapterBase)
        FieldUtil.set_adapters(stub_function, [stub_adapter])
        assert FieldUtil.get_adapters(stub_function) == [stub_adapter]

    def test_Should_return_none_When_get_adapters_is_called_and_adapters_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.get_adapters(stub_function) is None

    def test_Should_return_false_When_has_adapters_is_called_and_adapters_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.has_adapters(stub_function) is False

    def test_Should_return_true_When_has_adapters_is_called_and_adapters_is_set(
        self, stub_function
    ):
        adapter = MagicMock(AdapterBase)
        FieldUtil.set_adapters(stub_function, [adapter])
        assert FieldUtil.has_adapters(stub_function) is True


class TestName:
    def test_Should_set_name_When_set_name_is_called(self, stub_function):
        name = "name"
        FieldUtil.set_name(stub_function, name)
        assert getattr(stub_function, "name") == name

    def test_Should_return_name_When_get_name_is_called(self, stub_function):
        name = "name"
        FieldUtil.set_name(stub_function, name)
        assert FieldUtil.get_name(stub_function) == name

    def test_Should_raise_error_When_get_name_is_called_and_name_is_not_set(
        self, stub_function
    ):
        with pytest.raises(ValueError):
            FieldUtil.get_name(stub_function)

    def test_Should_return_true_When_has_name_is_called_and_name_is_set(
        self, stub_function
    ):
        FieldUtil.set_name(stub_function, "name")
        assert FieldUtil.has_name(stub_function) is True

    def test_Should_return_false_When_has_name_is_called_and_name_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.has_name(stub_function) is False


class TestValidationCallback:
    def test_Should_add_validation_callback_When_add_validation_callback_is_called(
        self, stub_function
    ):
        callback = MagicMock()
        stub_function = FieldUtil.add_validation_callback(stub_function, callback)
        assert getattr(stub_function, "validation_callbacks") == [callback]

    def test_Should_return_validation_callback_When_get_validation_callback_is_called(
        self, stub_function
    ):
        callback = MagicMock()
        FieldUtil.add_validation_callback(stub_function, callback)
        assert FieldUtil.get_validation_callbacks(stub_function) == [callback]

    def test_Should_return_empty_array_When_get_validation_callback_is_called_and_validation_callback_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.get_validation_callbacks(stub_function) == []

    def test_Should_return_multiple_validations_When_multiple_validations_are_added(
        self, stub_function
    ):
        callback1 = MagicMock()
        callback2 = MagicMock()
        stub_function = FieldUtil.add_validation_callback(stub_function, callback1)
        stub_function = FieldUtil.add_validation_callback(stub_function, callback2)
        assert FieldUtil.get_validation_callbacks(stub_function) == [
            callback1,
            callback2,
        ]


class TestOptional:
    def test_Should_set_optional_When_set_optional_is_called(self, stub_function):
        FieldUtil.set_optional(stub_function, True)
        assert getattr(stub_function, "optional") is True

    def test_Should_return_optional_When_is_optional_is_called(self, stub_function):
        FieldUtil.set_optional(stub_function, True)
        assert FieldUtil.is_optional(stub_function) is True

    def test_Should_return_false_When_is_optional_is_called_and_optional_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.is_optional(stub_function) is False


class TestTransformCallback:
    def test_Should_add_transform_callback_When_add_transform_callback_is_called(
        self, stub_function
    ):
        callback = MagicMock()
        stub_function = FieldUtil.add_transform_callback(stub_function, callback)
        assert getattr(stub_function, "transform_callbacks", callback)

    def test_Should_return_transform_callback_When_get_transform_callback_is_called(
        self, stub_function
    ):
        callback = MagicMock()
        stub_function = FieldUtil.add_transform_callback(stub_function, callback)
        assert FieldUtil.get_transform_callbacks(stub_function) == [callback]

    def test_Should_return_empty_array_When_get_transform_callback_is_called_and_transform_callback_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.get_transform_callbacks(stub_function) == []

    def test_Should_append_to_existing_transform_callbacks_When_multiple_decorated_with_multiple_callbacks(
        self, stub_function
    ):
        callback1 = MagicMock()
        callback2 = MagicMock()
        stub_function = FieldUtil.add_transform_callback(stub_function, callback1)
        stub_function = FieldUtil.add_transform_callback(stub_function, callback2)
        assert FieldUtil.get_transform_callbacks(stub_function) == [
            callback1,
            callback2,
        ]


class TestCacheResponse:
    def test_Should_set_cached_response_When_set_cached_response_is_called(
        self, stub_function
    ):
        response = MagicMock()
        FieldUtil.set_cached_response(stub_function, response)
        assert getattr(stub_function, "cached_response") == response

    def test_Should_return_cached_response_When_get_cached_response_is_called(
        self, stub_function
    ):
        response = MagicMock()
        FieldUtil.set_cached_response(stub_function, response)
        assert FieldUtil.get_cached_response(stub_function) == response

    def test_Should_raise_value_error_When_get_cached_response_is_called_and_cached_response_is_not_set(
        self, stub_function
    ):
        with pytest.raises(ValueError):
            FieldUtil.get_cached_response(stub_function)

    def test_Should_return_true_When_has_cached_response_is_called_and_cached_response_is_set(
        self, stub_function
    ):
        FieldUtil.set_cached_response(stub_function, MagicMock())
        assert FieldUtil.has_cached_response(stub_function) is True

    def test_Should_return_false_When_has_cached_response_is_called_and_cached_response_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.has_cached_response(stub_function) is False

    def test_Should_delete_cached_response_When_delete_cached_response_is_called(
        self, stub_function
    ):
        response = MagicMock()
        FieldUtil.set_cached_response(stub_function, response)
        FieldUtil.delete_cached_response(stub_function)
        assert FieldUtil.has_cached_response(stub_function) is False

    def test_Should_not_raise_error_When_delete_cached_response_is_called_and_cached_response_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.has_cached_response(stub_function) is False
        FieldUtil.delete_cached_response(stub_function)


class TestOriginalFunction:
    def test_Should_set_original_function_When_set_original_function_is_called(
        self, stub_function
    ):
        original_function = MagicMock()
        FieldUtil.set_original_function(stub_function, original_function)
        assert getattr(stub_function, "original_function") == original_function

    def test_Should_return_original_function_When_get_original_function_is_called(
        self, stub_function
    ):
        original_function = MagicMock()
        FieldUtil.set_original_function(stub_function, original_function)
        assert FieldUtil.get_original_function(stub_function) == original_function

    def test_Should_raise_value_error_When_get_original_function_is_called_and_original_function_is_not_set(
        self, stub_function
    ):
        with pytest.raises(ValueError):
            FieldUtil.get_original_function(stub_function)

    def test_Should_return_true_When_has_original_function_is_called_and_original_function_is_set(
        self, stub_function
    ):
        FieldUtil.set_original_function(stub_function, MagicMock())
        assert FieldUtil.has_original_function(stub_function) is True

    def test_Should_return_false_When_has_original_function_is_called_and_original_function_is_not_set(
        self, stub_function
    ):
        assert FieldUtil.has_original_function(stub_function) is False
