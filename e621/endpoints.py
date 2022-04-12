from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import E621API

from . import models


@dataclass
class BaseEndpoint:
    _api: "E621API"


class Posts(BaseEndpoint):
    pass


class Favorites(BaseEndpoint):
    pass


class PostFlags(BaseEndpoint):
    pass


class Tags(BaseEndpoint):
    pass


class TagAliases(BaseEndpoint):
    pass


class Notes(BaseEndpoint):
    pass


class Pools(BaseEndpoint):
    pass
