import pydantic
from backports.cached_property import cached_property


class BaseModel(pydantic.BaseModel):
    class Config:
        keep_untouched = (cached_property,)  # type: ignore
