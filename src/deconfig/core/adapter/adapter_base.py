from abc import ABC, abstractmethod
from typing import Callable, Any, TypeVar

T = TypeVar("T")


class AdapterBase(ABC):
    """
    Base class for all adapters.
    """

    @abstractmethod
    def get_field(self, field_name: str, method: Callable[..., T], *method_args, **method_kwargs) -> Any:
        """
        Use this method to initialize the field in configuration.
        If field is not present in config, AdapterError should be raised to indicate to library to try next adapter.

        :param field_name: Field name as passed in @field
        :param method: getter method - Use with FieldUtil to get additional properties from the field
        :param method_args: In case the response of getter is a method, arguments passed will be passed to the method
        :param method_kwargs: Same as method_args
        :return: Value if field is present, otherwise raise AdapterError
        :raises AdapterError: If field is not present, this indicates to library to try next adapter
        """
        pass
