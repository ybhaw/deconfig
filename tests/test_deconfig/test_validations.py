"""
Test cases for deconfig.validations module.
"""

import re
from enum import Enum
from unittest.mock import MagicMock

import pytest

from deconfig.validations import (
    validate,
    is_datatype,
    is_not_empty,
    is_in_range,
    matches_pattern,
    max_length,
    min_length,
    is_in_enum,
)


class TestValidate:
    def test_Should_validate_against_callback_When_decorated_with_validate(self):
        callable_stub = MagicMock()
        callable_stub.side_effect = [MagicMock(), ValueError]

        @validate(callable_stub)
        def stub_function():
            return 1

        response = stub_function()
        assert response == 1
        assert callable_stub.call_count == 1

        with pytest.raises(ValueError) as e:
            stub_function()

        assert str(e.value) == 'Validation failed for "stub_function" method.'
        assert callable_stub.call_count == 2

    # noinspection PyTypeChecker,PyArgumentList
    def test_Should_raise_type_error_When_callback_is_missing(self):
        with pytest.raises(TypeError) as e:
            validate(None)(lambda: None)
        assert str(e.value) == "Callback is required."

        with pytest.raises(TypeError) as e:
            validate()(lambda: None)  # pylint: disable=no-value-for-parameter
        assert (
            str(e.value)
            == "validate() missing 1 required positional argument: 'callback'"
        )

    # noinspection PyTypeChecker
    def test_Should_raise_type_error_When_callback_is_not_callable(self):
        with pytest.raises(TypeError) as e:
            validate(1)(lambda: None)
        assert str(e.value) == "Callback must be a callable."


class TestIsDatatype:
    @pytest.mark.parametrize(
        "datatype, response, is_valid",
        [
            (str, "foo", True),
            (str, 1, False),
            (int, 1, True),
            (int, "foo", False),
            (bool, True, True),
            (bool, 1, False),
            (float, 1.0, True),
            (float, 1, False),
        ],
    )
    def test_Should_validate_datatype_When_decorated_with_is_datatype(
        self, datatype, response, is_valid
    ):
        @is_datatype(datatype)
        def stub_function():
            return response

        if is_valid:
            assert stub_function() == response
        else:
            with pytest.raises(ValueError) as e:
                stub_function()
            assert str(e.value) == 'Validation failed for "stub_function" method.'


class TestIsNotEmpty:
    @pytest.mark.parametrize(
        "response, is_valid",
        [
            (1, True),
            ("foo", True),
            ("", False),
            (None, False),
            ([], False),
            ({}, False),
            ((), False),
        ],
    )
    def test_Should_validate_not_empty_When_decorated_with_is_not_empty(
        self, response, is_valid
    ):
        @validate(is_not_empty)
        def stub_function():
            return response

        if is_valid:
            assert stub_function() == response
        else:
            with pytest.raises(ValueError) as e:
                stub_function()
            assert str(e.value) == 'Validation failed for "stub_function" method.'


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    "response, start_value, end_value, left_inclusive, right_inclusive, is_valid",
    [
        (1, 0, 2, True, True, True),
        (1, 0, 2, False, True, True),
        (1, 0, 2, True, False, True),
        (1, 0, 2, False, False, True),
        (0, 0, 2, True, True, True),
        (0, 0, 2, False, True, False),
        (2, 0, 2, True, True, True),
        (2, 0, 2, True, False, False),
        (2, 0, 2, False, True, True),
        (2, 0, 2, False, False, False),
        (0, 1, 2, True, True, False),
        (0, 1, 2, False, True, False),
        (0, 1, 2, True, False, False),
        (0, 1, 2, False, False, False),
        (4, 1, 2, True, True, False),
        (4, 1, 2, False, True, False),
        (4, 1, 2, True, False, False),
        (4, 1, 2, False, False, False),
        ("41", "1", "5", False, False, True),
    ],
)
def test_Should_validate_in_range_When_decorated_with_is_in_range(
    response, start_value, end_value, left_inclusive, right_inclusive, is_valid
):
    @is_in_range(start_value, end_value, left_inclusive, right_inclusive)
    def stub_function():
        return response

    if is_valid:
        assert stub_function() == response
    else:
        with pytest.raises(ValueError) as e:
            stub_function()
        assert str(e.value) == 'Validation failed for "stub_function" method.'


@pytest.mark.parametrize(
    "response, pattern, is_valid",
    [
        ("foo", re.compile("foo"), True),
        ("foo", re.compile(r"bar"), False),
        ("foo", re.compile(r"fo*"), True),
        ("foo", re.compile(r"b.*"), False),
        ("foo", re.compile(r"b.*"), False),
        ("foo", re.compile(r"f.*"), True),
        ("foo", re.compile(r".*"), True),
        ("foo", re.compile(r".+"), True),
        ("", re.compile(r".*"), True),
    ],
)
def test_Should_validate_matches_pattern_When_decorated_with_matches_pattern(
    response, pattern, is_valid
):
    @matches_pattern(pattern)
    def stub_function():
        return response

    if is_valid:
        assert stub_function() == response
    else:
        with pytest.raises(ValueError) as e:
            stub_function()
        assert str(e.value) == 'Validation failed for "stub_function" method.'


@pytest.mark.parametrize(
    "response, max_length_value, is_valid",
    [
        ("foo", 3, True),
        ("foo", 2, False),
        ("foo", 4, True),
        ("foo", 0, False),
        ("foo", -1, False),
        ("", 0, True),
        ("", 1, True),
        ("", -1, False),
    ],
)
def test_Should_validate_max_length_When_decorated_with_max_length(
    response, max_length_value, is_valid
):
    @max_length(max_length_value)
    def stub_function():
        return response

    if is_valid:
        assert stub_function() == response
    else:
        with pytest.raises(ValueError) as e:
            stub_function()
        assert str(e.value) == 'Validation failed for "stub_function" method.'


@pytest.mark.parametrize(
    "response, min_length_value, is_valid",
    [
        ("foo", 3, True),
        ("foo", 2, True),
        ("foo", 4, False),
        ("foo", 0, True),
        ("foo", -1, True),
        ("", 0, True),
        ("", 1, False),
        ("", -1, True),
    ],
)
def test_Should_validate_min_length_When_decorated_with_min_length(
    response, min_length_value, is_valid
):
    @min_length(min_length_value)
    def stub_function():
        return response

    if is_valid:
        assert stub_function() == response
    else:
        with pytest.raises(ValueError) as e:
            stub_function()
        assert str(e.value) == 'Validation failed for "stub_function" method.'


def test_Should_check_value_is_in_enum_When_decorated_with_is_in_enum():
    class StubEnum(Enum):
        A = "A"
        B = "B"

    @is_in_enum(StubEnum)
    def stub_function(value):
        return value

    assert stub_function(StubEnum.A) == StubEnum.A
    with pytest.raises(ValueError) as e:
        assert stub_function("C")
    assert str(e.value) == 'Validation failed for "stub_function" method.'

    @is_in_enum(StubEnum, use_value=True)
    def stub_function_2(value):
        return value

    assert stub_function_2("A") == "A"
    with pytest.raises(ValueError) as e:
        assert stub_function_2("C")
    assert str(e.value) == 'Validation failed for "stub_function_2" method.'


@pytest.mark.parametrize(
    "import_name",
    [
        "is_datatype",
        "is_not_empty",
        "is_in_range",
        "matches_pattern",
        "max_length",
        "min_length",
        "is_in_enum",
        "__version__",
        "__license__",
        "__author__",
        "__description__",
    ],
)
def test_Should_expose_all_methods_and_constants_When_deconfig_validations_is_imported(
    import_name,
):
    import deconfig.validations as module  # pylint: disable=import-outside-toplevel

    assert hasattr(module, import_name)
