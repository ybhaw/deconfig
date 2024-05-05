"""
Unit tests for `deconfig.transformer` module.
"""

import pytest
from deconfig import field, config, optional, EnvAdapter, set_default_adapters
import deconfig.transformer as ts


@pytest.fixture(name="field_decorated_callable")
def fixture_field_decorated_callable():

    @field(name="stub_field")
    def callable_stub():
        """Stub callable"""

    return callable_stub


def _get_config_with_decorator(decorator, field_response):
    set_default_adapters(EnvAdapter())

    @config()
    class StubConfig:
        @decorator
        @optional()
        @field(name="stub_field")
        def stub_field(self):
            return field_response

    return StubConfig()


class TestTransform:

    def test_Should_return_same_function_When_decorated_with_transform(
        self, field_decorated_callable
    ):
        callable_response = ts.transform(lambda x: x)(field_decorated_callable)
        assert callable_response == field_decorated_callable

    def test_Should_add_transform_attribute_When_decorated_with_transform(
        self, field_decorated_callable
    ):
        callable_response = ts.transform(lambda x: x)(field_decorated_callable)
        assert hasattr(callable_response, "transform_callbacks")


class TestString:
    def test_Should_return_same_function_When_decorated_with_transformer_callable(
        self, field_decorated_callable
    ):
        callable_response = ts.string()(field_decorated_callable)
        assert callable_response == field_decorated_callable
        assert hasattr(callable_response, "transform_callbacks")

    @pytest.mark.parametrize(
        "field_response, transformed_response",
        [
            (None, None),
            ("", ""),
            ("test", "test"),
            (1, "1"),
            (1.0, "1.0"),
            (True, "True"),
            (False, "False"),
        ],
    )
    def test_Should_return_transformed_response_When_decorated_and_cast_null_is_false(
        self, field_response, transformed_response
    ):
        config_instance = _get_config_with_decorator(ts.string(), field_response)
        assert config_instance.stub_field() == transformed_response

    def test_Should_cast_null_to_string_When_decorated_and_cast_null_is_true(self):
        config_instance = _get_config_with_decorator(ts.string(cast_null=True), None)
        assert config_instance.stub_field() == "None"


class TestInteger:
    def test_Should_return_same_function_When_decorated_with_transformer_callable(
        self, field_decorated_callable
    ):
        callable_response = ts.integer()(field_decorated_callable)
        assert callable_response == field_decorated_callable
        assert hasattr(callable_response, "transform_callbacks")

    @pytest.mark.parametrize(
        "field_response, transformed_response",
        [(None, None), (1, 1), (1.0, 1), (True, 1), (False, 0)],
    )
    def test_Should_return_transformed_response_When_decorated_and_cast_null_is_false(
        self, field_response, transformed_response
    ):
        config_instance = _get_config_with_decorator(ts.integer(), field_response)
        assert config_instance.stub_field() == transformed_response

    def test_Should_raise_value_error_When_cannot_cast_to_int(self):
        config_instance = _get_config_with_decorator(ts.integer(), "test")
        with pytest.raises(ValueError):
            config_instance.stub_field()

    def test_Should_return_none_When_cast_null_is_default_or_false(self):
        config_instance = _get_config_with_decorator(ts.integer(), None)
        assert config_instance.stub_field() is None
        config_instance = _get_config_with_decorator(ts.integer(cast_null=False), None)
        assert config_instance.stub_field() is None

    def test_Should_raise_value_error_When_cast_null_is_true(self):
        config_instance = _get_config_with_decorator(ts.integer(cast_null=True), None)
        with pytest.raises(TypeError):
            config_instance.stub_field()


class TestFloating:
    def test_Should_return_same_function_When_decorated_with_transformer_callable(
        self, field_decorated_callable
    ):
        callable_response = ts.floating()(field_decorated_callable)
        assert callable_response == field_decorated_callable
        assert hasattr(callable_response, "transform_callbacks")

    @pytest.mark.parametrize(
        "field_response, transformed_response",
        [(None, None), (1, 1.0), (1.0, 1.0), (True, 1.0), (False, 0.0)],
    )
    def test_Should_return_transformed_response_When_decorated_and_cast_null_is_false(
        self, field_response, transformed_response
    ):
        config_instance = _get_config_with_decorator(ts.floating(), field_response)
        assert config_instance.stub_field() == transformed_response

    def test_Should_raise_value_error_When_cannot_cast_to_float(self):
        config_instance = _get_config_with_decorator(ts.floating(), "test")
        with pytest.raises(ValueError):
            config_instance.stub_field()

    def test_Should_return_none_When_cast_null_is_default_or_false(self):
        config_instance = _get_config_with_decorator(ts.floating(), None)
        assert config_instance.stub_field() is None
        config_instance = _get_config_with_decorator(ts.floating(cast_null=False), None)
        assert config_instance.stub_field() is None

    def test_Should_raise_value_error_When_cast_null_is_true(self):
        config_instance = _get_config_with_decorator(ts.floating(cast_null=True), None)
        with pytest.raises(TypeError):
            config_instance.stub_field()


class TestBoolean:
    def test_Should_return_same_function_When_decorated_with_transformer_callable(
        self, field_decorated_callable
    ):
        callable_response = ts.boolean()(field_decorated_callable)
        assert callable_response == field_decorated_callable
        assert hasattr(callable_response, "transform_callbacks")

    @pytest.mark.parametrize(
        "field_response, transformed_response",
        [
            (None, None),
            (1, True),
            (1.0, True),
            (True, True),
            (False, False),
            (0, False),
            (0.0, False),
            ("test", True),
            ("false", True),
            ("False", True),
            ("", False),
        ],
    )
    def test_Should_return_transformed_response_When_decorated_and_cast_null_is_false(
        self, field_response, transformed_response
    ):
        config_instance = _get_config_with_decorator(ts.boolean(), field_response)
        assert config_instance.stub_field() == transformed_response

    def test_Should_return_none_When_cast_null_is_default_or_false(self):
        config_instance = _get_config_with_decorator(ts.boolean(), None)
        assert config_instance.stub_field() is None
        config_instance = _get_config_with_decorator(ts.boolean(cast_null=False), None)
        assert config_instance.stub_field() is None


class TestCommaSeparatedArrayString:
    def test_Should_return_same_function_When_decorated_with_transformer_callable(
        self, field_decorated_callable
    ):
        callable_response = ts.comma_separated_array_string(str)(
            field_decorated_callable
        )
        assert callable_response == field_decorated_callable
        assert hasattr(callable_response, "transform_callbacks")

    @pytest.mark.parametrize(
        "field_response, transformed_response",
        [
            (None, []),
            ("", [""]),
            ("test", ["test"]),
            ("1,2,3", ["1", "2", "3"]),
            (1, ["1"]),
            (1.0, ["1.0"]),
            (True, ["True"]),
            (False, ["False"]),
            ("1.1,2.2,2\\,3", ["1.1", "2.2", "2\\", "3"]),
            (b"1,2,3", ["1", "2", "3"]),
        ],
    )
    def test_Should_return_transformed_response_When_decorated_and_cast_null_is_false(
        self, field_response, transformed_response
    ):
        config_instance = _get_config_with_decorator(
            ts.comma_separated_array_string(str), field_response
        )
        assert config_instance.stub_field() == transformed_response

    def test_Should_return_none_When_cast_null_is_default_or_false(self):
        config_instance = _get_config_with_decorator(
            ts.comma_separated_array_string(str), None
        )
        assert config_instance.stub_field() == []
        config_instance = _get_config_with_decorator(
            ts.comma_separated_array_string(str, cast_null=False), None
        )
        assert config_instance.stub_field() == []

    def test_Should_raise_value_error_When_cannot_cast_to_callable_in_list(self):
        config_instance = _get_config_with_decorator(
            ts.comma_separated_array_string(int), "hello"
        )
        with pytest.raises(ValueError):
            config_instance.stub_field()

    def test_Should_cast_returned_value_to_string_before_splitting_When_returned_value_is_not_string(
        self,
    ):
        config_instance = _get_config_with_decorator(
            ts.comma_separated_array_string(int), 1
        )
        assert config_instance.stub_field() == [1]

    @pytest.mark.parametrize(
        "cast_callback, field_response, transformed_response",
        [
            (str, "1,2,3", ["1", "2", "3"]),
            (int, "1,2,3", [1, 2, 3]),
            (bool, "1,,1", [True, False, True]),
            (float, "1.1,2.2,3.3", [1.1, 2.2, 3.3]),
            (lambda x: x != "0", "1,0,1", [True, False, True]),
        ],
    )
    def test_Should_cast_to_cast_callback_When_returned_values_can_be_casted(
        self, cast_callback, field_response, transformed_response
    ):
        config_instance = _get_config_with_decorator(
            ts.comma_separated_array_string(cast_callback), field_response
        )
        assert config_instance.stub_field() == transformed_response
