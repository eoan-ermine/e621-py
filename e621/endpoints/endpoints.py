from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Type, TypeVar

from ..base_model import BaseModel

if TYPE_CHECKING:
    from ..api import E621API


Model = TypeVar("Model", bound=BaseModel)


class BaseEndpoint(Generic[Model]):
    _model: Type[Model]
    _root_entity_name: str
    _url: str

    def __init__(self, api: "E621API") -> None:
        self._api = api

    def _default_get(self, identifier: Any, **kwargs: Any) -> Model:
        return self._model.from_response(self._api.session.get(f"{self._url}/{identifier}", **kwargs), self._api)

    def _default_search(
        self, params: Dict[str, Any], limit: Optional[int], page: int = 1, ignore_pagination=False
    ) -> List[Model]:
        # ? Seems like a potential source of a bug
        params.update({"limit": limit, "page": page})
        if ignore_pagination:
            return self._model.from_list(
                self._api.session.paginated_get(self._url, params, self._root_entity_name), self._api
            )
        else:
            return self._model.from_response(self._api.session.get(self._url, params=params), self._api, expect=list)

    def _default_create(self, params: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Model:
        return self._model.from_response(self._api.session.post(self._url, params=params, files=files), self._api)

    def _default_update(self, identifier: Any, params: Dict[str, Any]) -> None:
        self._api.session.patch(f"{self._url}/{identifier}", params=params)

    def _default_delete(self, identifier: Any, params: Optional[Dict[str, Any]] = None) -> None:
        self._api.session.delete(f"{self._url}/{identifier}", params=params)
