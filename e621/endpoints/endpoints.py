import inspect
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Type, TypeVar

from e621.util import camel_to_snake

from ..base_model import BaseModel

if TYPE_CHECKING:
    from ..api import E621


Model = TypeVar("Model", bound=BaseModel)


class BaseEndpoint(Generic[Model]):
    _model: Type[Model]
    _root_entity_name: str
    _url: str

    def __init__(self, api: "E621") -> None:
        self._api = api

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        class_name_in_snake_case = camel_to_snake(cls.__name__)
        if getattr(cls, "_root_entity_name", None) is None:
            cls._root_entity_name = class_name_in_snake_case
        if getattr(cls, "_url", None) is None:
            cls._url = class_name_in_snake_case

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

    def _magical_search(self, limit, page, ignore_pagination, *args: Any) -> List[Model]:
        return self._default_search(
            {f"search[{argname}]": arg for argname, arg in zip(inspect.signature(self.search).parameters, args)},
            limit,
            page,
            ignore_pagination,
        )

    def _default_create(self, params: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Model:
        return self._model.from_response(self._api.session.post(self._url, params=params, files=files), self._api)

    def _default_update(self, identifier: Any, params: Dict[str, Any]) -> None:
        self._api.session.patch(f"{self._url}/{identifier}", params=params)

    def _default_delete(self, identifier: Any, params: Optional[Dict[str, Any]] = None) -> None:
        self._api.session.delete(f"{self._url}/{identifier}", params=params)
