from typing import Callable, TypeVar, List

T = TypeVar("T")
U = TypeVar("U")


def transform(callback: Callable[[T], U]) -> Callable[..., T]:
    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        func.transform_callback = callback
        return func
    return wrapper


def cast_custom(callback: Callable[[T], T], cast_null: bool = False) -> Callable[[U], Callable[..., U]]:
    def callback_wrapper(response: U) -> T:
        if response is None and cast_null is False:
            return None
        return callback(response)

    return transform(callback_wrapper)


def string(cast_null: bool = False) -> Callable[..., Callable[..., str]]:
    return cast_custom(str, cast_null)


def integer(cast_null: bool = False) -> Callable[..., Callable[..., int]]:
    return cast_custom(int, cast_null)


def floating(cast_null: bool = False) -> Callable[..., Callable[..., float]]:
    return cast_custom(float, cast_null)


def boolean(cast_null: bool = False) -> Callable[..., Callable[..., bool]]:
    return cast_custom(bool, cast_null)


def comma_separated_array_string(element_cast: Callable[[T], T], cast_null: bool = False) -> Callable[[U], Callable[..., List[T]]]:
    def callback(response: U) -> List[T]:
        if response is None and cast_null is False:
            return []
        if isinstance(response, bytes):
            response = response.decode("utf-8")
        if not isinstance(response, str):
            response = str(response)
        return [element_cast(x) for x in response.split(",")]

    return transform(callback)


__all__ = ["transform", "string", "integer", "floating", "boolean", "comma_separated_array_string"]
