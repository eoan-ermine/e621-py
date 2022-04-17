import functools
import inspect
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union
from typing_extensions import ParamSpec
from e621.util import camel_to_snake

from ..base_model import BaseModel

if TYPE_CHECKING:
    from ..api import E621


Model = TypeVar("Model", bound=BaseModel)


_METHOD_MAPPER = {
    "create": "_magical_create",
    "get": "_default_get",
    "search": "_magical_search",
    "update": "_magical_update",
    "delete": "_default_delete",
}


class BaseEndpoint(Generic[Model]):
    _model: Type[Model]
    _root_entity_name: str
    _url: str
    _model_snake_case_name: str

    def __init__(self, api: "E621") -> None:
        self._api = api

    def __init_subclass__(cls, *, generate=()) -> None:
        super().__init_subclass__()
        class_name_in_snake_case = camel_to_snake(cls.__name__)
        if getattr(cls, "_root_entity_name", None) is None:
            cls._root_entity_name = class_name_in_snake_case
        if getattr(cls, "_url", None) is None:
            cls._url = class_name_in_snake_case
        cls._model_snake_case_name = camel_to_snake(cls._model.__name__)
        for method_name in generate:
            setattr(cls, method_name, _generate_endpoint_method(cls, getattr(cls, method_name)))

    def _default_get(self, identifier: Any, **kwargs: Any) -> Model:
        return self._model.from_response(self._api.session.get(f"{self._url}/{identifier}", **kwargs), self._api)

    def _default_search(
        self, params: Dict[str, Any], limit: Optional[int], page: int = 1, ignore_pagination=False
    ) -> List[Model]:
        # In case the user reuses the same set of params
        params = params.copy()
        params.update({"limit": limit, "page": page})
        if ignore_pagination:
            return self._model.from_list(
                self._api.session.paginated_get(self._url, params, self._root_entity_name), self._api
            )
        else:
            return self._model.from_response(self._api.session.get(self._url, params=params), self._api, expect=list)

    def _default_create(self, params: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Model:
        return self._model.from_response(self._api.session.post(self._url, params=params, files=files), self._api)

    def _default_update(self, identifier: Union[str, int], params: Dict[str, Any]) -> None:
        self._api.session.patch(f"{self._url}/{identifier}", params=params)

    def _default_delete(self, identifier: Union[str, int], **kwargs: Any) -> None:
        self._api.session.delete(f"{self._url}/{identifier}", **kwargs)

    def _magical_search(self, *raw_args: Any, _param_prefix="search") -> List[Model]:
        """A default search that automatically generates search params from self.search definition"""
        *args, limit, page, ignore_pagination = raw_args
        return self._magical_method(
            self.search, self._default_search, _param_prefix, (), (limit, page, ignore_pagination), args
        )

    def _magical_create(self, *args: Any, _param_prefix=None) -> Model:
        """A default create that automatically generates create params from self.create definition"""
        if _param_prefix is None:
            _param_prefix = self._model_snake_case_name
        return self._magical_method(self.create, self._default_create, _param_prefix, (), (), args)

    def _magical_update(self, identifier: Union[str, int], *args: Any, _param_prefix=None) -> Model:
        if _param_prefix is None:
            _param_prefix = self._model_snake_case_name
        return self._magical_method(self.update, self._default_update, _param_prefix, (identifier,), (), args, 1)

    def _magical_method(
        self,
        method: Callable,
        default_method: Callable,
        param_prefix: str,
        before_meta_args: Sequence[Any],
        after_meta_args: Sequence[Any],
        args: Any,
        arg_offset: int = 0,
    ) -> Any:
        parameters = list(inspect.signature(method).parameters)
        return default_method(
            *before_meta_args,
            {f"{param_prefix}[{argname}]": arg for argname, arg in zip(parameters[arg_offset:], args)},
            *after_meta_args,
        )


_P = ParamSpec("P")
_T = TypeVar("T")


def _generate_endpoint_method(cls: Type[BaseEndpoint], method: Callable[_P, _T]) -> Callable[_P, _T]:
    magical_method = getattr(cls, _METHOD_MAPPER[method.__name__])
    method_signature = inspect.signature(method)

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        bound_signature = method_signature.bind(self, *args, **kwargs)
        bound_signature.apply_defaults()
        return magical_method(*bound_signature.arguments.values())

    return wrapper
