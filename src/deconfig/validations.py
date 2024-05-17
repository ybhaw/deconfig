"""
A simple validation library for Python.
Useful to validate configurations, but can be used with any method.

Example Usage:
    @is_string()
    @field(name="app_setting")
    def get_app_settings() -> str:
        return "app_settings"
"""

from enum import Enum
from typing import Callable, TypeVar, Any, Type, Pattern, Optional
from deconfig.__version__ import __version__, __author__, __license__

__description__ = "A simple validation library for Python."

from deconfig.core import is_callable

T = TypeVar("T")
Comparable = TypeVar("Comparable")


def validate(callback: Callable[[Any], None]) -> Callable[..., T]:
    """
    Validate the output of what a method returns.
    This should be used as a decorator.

    Example:
        def is_string(response: Any) -> None:
            if not isinstance(response, str):
                raise ValueError("Response is not a string.")

        @validate(is_string)
        def get_foo() -> str:
            return "foo"
    """
    is_callable(callback)

    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        def validate_and_call(*args, **kwargs):
            response = func(*args, **kwargs)
            try:
                callback(response)
            except ValueError as e:
                raise ValueError(
                    f'Validation failed for "{func.__name__}" method.'
                ) from e
            return response

        validate_and_call: func = validate_and_call
        return validate_and_call

    return wrapper


def is_datatype(datatype: Type) -> Callable[..., None]:
    """
    Validate the output of what a method returns is of a specific datatype.
    :param datatype: Type of the datatype to validate.
    :raises ValueError: If the response is not of the specified datatype.
    """

    def validation_callback(response: Any) -> None:
        if not isinstance(response, datatype):
            raise ValueError(f'Response is not a "{datatype.__name__}".')

    return validate(validation_callback)


def is_not_empty(response: Any) -> None:
    """
    Validate the output of what a method returns is not empty.
    :param response:
    :raises ValueError: If the response is empty.
    """
    if not response:
        raise ValueError("Response is empty.")


def is_in_range(
    min_value: Comparable,
    max_value: Comparable,
    left_inclusive: bool = True,
    right_inclusive: bool = True,
) -> Callable[..., None]:
    """
    Validate the output of what a method returns is within a range.
    :param min_value: Minimum value.
    :param max_value: Maximum value.
    :param left_inclusive: If the minimum value is inclusive.
    :param right_inclusive: If the maximum value is inclusive.
    :raises ValueError: If the response is not within the range.
    """

    def validation_callback(response: Any) -> None:
        if min_value is not None:
            if left_inclusive and response < min_value:
                raise ValueError(f"Response is less than {min_value}.")
            if not left_inclusive and response <= min_value:
                raise ValueError(f"Response is less than or equal to {min_value}.")
        if max_value is not None:
            if right_inclusive and response > max_value:
                raise ValueError(f"Response is greater than {max_value}.")
            if not right_inclusive and response >= max_value:
                raise ValueError(f"Response is greater than or equal to {max_value}.")

    return validate(validation_callback)


def matches_pattern(pattern: Pattern) -> Callable[..., None]:
    """
    Validate the output of what a method returns matches a pattern.
    :param pattern: regex pattern to match.
    :raises ValueError: If the response does not match the pattern.
    """

    def validation_callback(response: Any) -> None:
        if not pattern.match(response):
            raise ValueError("Response does not match the pattern.")

    return validate(validation_callback)


def max_length(length: int) -> Callable[..., None]:
    """
    Validate the output of what a method returns is less than a specific length.
    :param length: Maximum length (inclusive).
    :raises ValueError: If the response length is greater than the specified length.
    """

    def validation_callback(response: Any) -> None:
        if len(response) > length:
            raise ValueError(f"Response length is greater than {length}.")

    return validate(validation_callback)


def min_length(length: int) -> Callable[..., None]:
    """
    Validate the output of what a method returns is greater than a specific length.
    :param length: Minimum length (inclusive).
    :raises ValueError: If the response length is less than the specified length.
    """

    def validation_callback(response: Any) -> None:
        if len(response) < length:
            raise ValueError(f"Response length is less than {length}.")

    return validate(validation_callback)


def is_in_enum(
    enum: Type[Enum], use_value: Optional[bool] = False
) -> Callable[..., None]:
    """
    Validate the output of what a method returns is in an Enum.
    :param enum: Enum to validate against.
    :param use_value: If the Enum value should be used instead of the Enum.
    :raises ValueError: If the response is not in the Enum.
    """

    def validation_callback(response: Any) -> None:
        if use_value:
            if response not in [e.value for e in enum]:
                raise ValueError("Response is not in the enum.")
        else:
            if not isinstance(response, enum):
                raise ValueError("Response is not in the enum.")

    return validate(validation_callback)


__all__ = [
    "validate",
    "is_datatype",
    "is_not_empty",
    "is_in_range",
    "matches_pattern",
    "max_length",
    "min_length",
    "is_in_enum",
    "__version__",
    "__author__",
    "__description__",
    "__license__",
]
