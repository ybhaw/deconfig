"""
This module contains decorators that can be used to transform
the values derived from configuration or default values.

Example Usage:

```python
@config()
class ExampleConfig:
    @string(cast_null=True)
    def get_foo(self) -> Optional[str]:
        return None # Returns "None"

    @transform(lambda x: x.upper())
    def get_bar(self) -> str:
        return "hello" # Returns "HELLO"
```
"""

from typing import Callable, TypeVar, List
from deconfig.__version__ import __version__, __author__, __license__

__description__ = "A simple transformation library for Python."

from deconfig.core import is_callable

T = TypeVar("T")
U = TypeVar("U")


def transform(callback: Callable[[T], U]) -> Callable[..., T]:
    """
    Adds a transform callback to be used when deriving configuration value.
    """
    is_callable(callback)

    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        def transform_and_call(*args, **kwargs):
            response = func(*args, **kwargs)
            return callback(response)

        transform_and_call: func = transform_and_call
        return transform_and_call

    return wrapper


def cast_datatype(
    callback: Callable[[T], T], cast_null: bool = False
) -> Callable[[U], Callable[..., U]]:
    """
    Casts response using custom callback.

    Parameters:
        callback: Function that will cast response.
        cast_null: If True and if response is None, None will be returned.

    Example Usage:
        ```
        @cast_custom(lambda x: lower(str(x)) == "true", cast_null=False)
        def get_foo(self) -> Optional[str]:
            return None

        # Returns True if response is "true", False otherwise.
        ```
    """

    def callback_wrapper(response: U) -> T:
        if response is None and cast_null is False:
            return None
        return callback(response)

    return transform(callback_wrapper)


def string(cast_null: bool = False) -> Callable[..., Callable[..., str]]:
    """
    Casts response to string.

    Parameters:
        cast_null: If True and if response is None, None will be returned.

    Example Usage:
        ```
        @string()
        def get_foo(self) -> Optional[str]:
            return None
        ```

    Example Outputs with cast_null=False:
        * "hello" -> "hello"
        * 0 -> "0"
        * 1 -> "1"
        * None -> None
    """
    return cast_datatype(str, cast_null)


def integer() -> Callable[..., Callable[..., int]]:
    """
    Casts response to integer.

    Raises:
        ValueError: If response is not a valid integer.

    Example Usage:
        ```
        @integer()
        def get_foo(self) -> Optional[str]:
            return None
        ```

    Example Outputs with cast_null=False:
        * "0" -> 0
        * 0 -> 0
        * 1 -> 1
        * "1.1" -> 1
        * "hello" -> Raises ValueError
        * None -> None
    """
    return cast_datatype(int)


def floating() -> Callable[..., Callable[..., float]]:
    """
    Casts response to float.

    Raises:
        ValueError: If response is not a valid float.

    Example Usage:
        ```
        @floating()
        def get_foo(self) -> Optional[str]:
            return None
        ```

    Example Outputs with cast_null=False:
        * "0" -> 0.0
        * 0 -> 0.0
        * 1 -> 1.0
        * "1.1" -> 1.1
        * "hello" -> Raises ValueError
        * None -> None
    """
    return cast_datatype(float)


def boolean(cast_null: bool = False) -> Callable[..., Callable[..., bool]]:
    """
    Casts response to boolean.

    Parameters:
        cast_null: If True and if response is None, None will be returned.

    Example Usage:
        ```
        @boolean()
        def get_foo(self) -> Optional[str]:
            return None
        ```

    Example Outputs with cast_null=False:
        * "" -> False
        * "0" -> True
        * 0 -> False
        * 1 -> True
        * "true" -> True
        * "false" -> True
        * True -> True
        * False -> False
        * [] -> False
        * [1] -> True
        * None -> None
    """
    return cast_datatype(bool, cast_null)


def comma_separated_array_string(
    element_cast: Callable[[T], T], cast_null: bool = False
) -> Callable[[U], Callable[..., List[T]]]:
    """
    Creates a comma separated list out of the configuration value.

    Parameters:
        element_cast: Function that will cast each element of the list.
        cast_null: If True and if response is None, None will be returned.

    Example:
        ```
        @comma_separated_array_string(element_cast=int)
        def get_foo(self) -> Optional[str]:
            return None
        ```

        If the configuration value is "1,2,3", the getter will return [1, 2, 3].
    """

    def callback(response: U) -> List[T]:
        if response is None and cast_null is False:
            return []
        if isinstance(response, bytes):
            response = response.decode("utf-8")
        if not isinstance(response, str):
            response = str(response)
        return [element_cast(x) for x in response.split(",")]

    return transform(callback)


__all__ = [
    "transform",
    "string",
    "integer",
    "floating",
    "boolean",
    "comma_separated_array_string",
    "cast_datatype",
    "__version__",
    "__author__",
    "__license__",
    "__description__",
]
