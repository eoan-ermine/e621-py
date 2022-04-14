from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, List, Union
import pydantic
import inspect


if TYPE_CHECKING:
    from ..api import E621API


@dataclass
class BaseEndpoint:
    _api: "E621API"

    def __init_subclass__(cls, *, validate_args: Union[bool, List[str]] = True) -> None:
        super().__init_subclass__()
        if validate_args:
            if isinstance(validate_args, bool):
                methods_to_validate = [k for k, v in cls.__dict__.items() if inspect.ismethod(v)]
            else:
                methods_to_validate = validate_args
            for method_name in methods_to_validate:
                setattr(cls, method_name, optional_validate_arguments(getattr(cls, method_name)))

    def _get_factory(self, endpoint: str) -> "BaseEndpoint":
        return self._api.__getattribute__(endpoint)()

    def _search_factory(self, endpoint: str, **kwargs) -> "BaseEndpoint":
        return self._api.__getattribute__(endpoint)(**kwargs)
