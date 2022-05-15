from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, overload

import pydantic
import requests
from backports.cached_property import cached_property
from typing_extensions import Self

if TYPE_CHECKING:
    from .api import E621


class BaseModel(pydantic.BaseModel):
    if TYPE_CHECKING:
        e621api: E621
    else:
        e621api: Any

    class Config:
        keep_untouched = (cached_property,)  # type: ignore

    @classmethod
    def from_list(cls, list: List[Dict[str, Any]], api: "E621") -> List[Self]:
        return [cls(**obj, e621api=api) for obj in list]

    @classmethod
    @overload
    def from_response(cls, response: requests.Response, e621api: "E621", expect: Type[Dict[Any, Any]] = dict) -> Self:
        ...

    @classmethod
    @overload
    def from_response(
        cls,
        response: requests.Response,
        e621api: "E621",
        expect: Type[List[Any]] = dict,  # type: ignore
    ) -> List[Self]:
        ...

    @classmethod
    def from_response(
        cls,
        response: requests.Response,
        e621api: "E621",
        expect: Union[Type[Dict[Any, Any]], Type[List[Any]]] = dict,
    ) -> Union[Self, List[Self]]:
        json: Union[Dict[Any, Any], List[Any]] = response.json()
        # {"post": {<post_info>}} or {"posts": [{<post_info>}, ...]}
        if isinstance(json, dict) and len(cls.schema()["required"]) > len(json) and len(json) == 1:
            json = json[list(json)[0]]

        if isinstance(json, list) and expect is list:
            return cls.from_list(json, e621api)
        elif isinstance(json, dict) and expect is dict:
            return cls(**json, e621api=e621api)
        else:
            raise TypeError(f"response.json() returned an unexpected object: {json}")
