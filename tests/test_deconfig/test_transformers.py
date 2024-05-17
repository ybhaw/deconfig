"""
Test cases for deconfig.transformer module.
"""

from unittest.mock import MagicMock

import pytest

from deconfig.transformer import (
    transform,
    cast_datatype,
    string,
    integer,
    boolean,
    floating,
    comma_separated_array_string,
)


class TestTransform:
    def test_Should_return_the_response_of_transformer_When_decorated_with_transformer(
        self,
    ):
        transformer_stub = MagicMock()
        response = MagicMock()

        @transform(transformer_stub)
        def stub_function():
            return response

        assert stub_function() == transformer_stub.return_value
        transformer_stub.assert_called_once_with(response)

    # noinspection PyArgumentList,PyTypeChecker
    def test_Should_raise_type_error_When_transformer_is_missing(self):
        with pytest.raises(TypeError) as e:
            transform(None)(lambda: None)
        assert str(e.value) == "Callback is required."

        with pytest.raises(TypeError) as e:
            transform()(lambda: None)  # pylint: disable=no-value-for-parameter
        assert (
            str(e.value)
            == "transform() missing 1 required positional argument: 'callback'"
        )

    # noinspection PyTypeChecker
    def test_Should_raise_type_error_When_transformer_is_not_callable(self):
        with pytest.raises(TypeError) as e:
            transform(1)(lambda: None)
        assert str(e.value) == "Callback must be a callable."


@pytest.mark.parametrize(
    "datatype, response, expected_response, cast_null",
    [
        (int, 1, 1, False),
        (int, "1", 1, False),
        (str, 1, "1", False),
        (str, "foo", "foo", False),
        (bool, 1, True, False),
        (bool, "true", True, False),
        (bool, "false", True, False),
        (str, None, None, False),
        (str, None, "None", True),
    ],
)
def test_Should_cast_response_to_datatype_When_decorated_with_cast_datatype(
    datatype, response, expected_response, cast_null
):
    @cast_datatype(datatype, cast_null)
    def stub_function():
        return response

    assert stub_function() == expected_response


@pytest.mark.parametrize(
    "decorator, response, cast_null, expected_response",
    [
        (string, "foo", False, "foo"),
        (string, 1, False, "1"),
        (string, None, True, "None"),
        (string, None, False, None),
    ],
)
def test_Should_cast_response_to_string_When_decorated_with_string(
    decorator, response, cast_null, expected_response
):
    @decorator(cast_null)
    def stub_function():
        return response

    assert stub_function() == expected_response


@pytest.mark.parametrize(
    "decorator, response, expected_response",
    [
        (integer, "1", 1),
        (integer, 1, 1),
        (integer, None, None),
        (integer, 1.0, 1),
        (integer, True, 1),
    ],
)
def test_Should_cast_response_to_integer_When_decorated_with_integer(
    decorator, response, expected_response
):
    @decorator()
    def stub_function():
        return response

    assert stub_function() == expected_response


@pytest.mark.parametrize(
    "decorator, response, cast_null, expected_response",
    [
        (boolean, "true", False, True),
        (boolean, "false", False, True),
        (boolean, 1, False, True),
        (boolean, 0, False, False),
        (boolean, None, True, False),
        (boolean, None, False, None),
    ],
)
def test_Should_cast_response_to_boolean_When_decorated_with_boolean(
    decorator, response, cast_null, expected_response
):
    @decorator(cast_null)
    def stub_function():
        return response

    assert stub_function() == expected_response


@pytest.mark.parametrize(
    "decorator, response, expected_response",
    [
        (floating, "1.0", 1.0),
        (floating, 1, 1.0),
        (floating, None, None),
        (floating, "1e5", 100000.0),
        (floating, True, 1.0),
    ],
)
def test_Should_cast_response_to_float_When_decorated_with_floating(
    decorator, response, expected_response
):
    @decorator()
    def stub_function():
        return response

    assert stub_function() == expected_response


@pytest.mark.parametrize(
    "response, datatype, cast_null, expected_value",
    [
        ("foo", str, False, ["foo"]),
        ("foo,bar", str, False, ["foo", "bar"]),
        ("1,2", int, False, [1, 2]),
        ("1,2", str, False, ["1", "2"]),
        ("1,2", float, False, [1.0, 2.0]),
        ("", str, False, [""]),
        (None, str, True, ["None"]),
        (None, str, False, []),
        (b"foo,bar", str, False, ["foo", "bar"]),
    ],
)
def test_Should_cast_response_to_comma_separated_array_string_When_decorated_with_comma_separated_array_string(
    response, datatype, cast_null, expected_value
):
    @comma_separated_array_string(datatype, cast_null)
    def stub_function():
        return response

    assert stub_function() == expected_value


@pytest.mark.parametrize(
    "import_name",
    [
        "transform",
        "cast_datatype",
        "string",
        "integer",
        "boolean",
        "floating",
        "comma_separated_array_string",
        "__version__",
        "__license__",
        "__author__",
        "__description__",
    ],
)
def test_Should_import_transformers_When_imported_from_deconfig_transformer(
    import_name,
):
    import deconfig.transformer as module  # pylint: disable=import-outside-toplevel

    assert hasattr(module, import_name)
