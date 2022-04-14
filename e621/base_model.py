from typing import List, Dict, Any, Type, Union, overload
from typing_extensions import Self
import pydantic
from backports.cached_property import cached_property
import requests


class BaseModel(pydantic.BaseModel):
    class Config:
        keep_untouched = (cached_property,)  # type: ignore

    @classmethod
    def from_list(cls, list: List[Dict[str, Any]]) -> List[Self]:
        return [cls.parse_obj(obj) for obj in list]

    @classmethod
    @overload
    def from_response(cls, response: requests.Response, expect: Type[list]) -> List[Self]:
        ...

    @classmethod
    @overload
    def from_response(cls, response: requests.Response, expect: Type[dict]) -> Self:
        ...

    @classmethod
    def from_response(cls, response: requests.Response, expect: Union[Type[dict], Type[list]]):
        json = response.json()
        # {"post": {<post_info>}} or {"posts": [{<post_info>}, ...]}
        if isinstance(json, dict) and len(cls.schema()["required"]) > len(json) and len(json) == 1:
            json = json[list(json)[0]]

        if isinstance(json, list) and expect is list:
            return cls.from_list(json)
        elif isinstance(json, dict) and expect is dict:
            return cls.parse_obj(json)
        else:
            raise TypeError(f"response.json() returned an unexpected object: {json}")
