from typing import Iterable, Optional, Set, Tuple, TypeVar

from backports.cached_property import cached_property

from . import endpoints
from .session import ApiKey, SimpleSession, Username

_T = TypeVar("_T")

# TODO: Move this somewhere more appropriate
class BlackList(Set[str]):
    def intersects(self, iterable: Iterable[str]) -> bool:
        for val in self:
            if " " in val and all(v in iterable for v in val.replace("  ", " ").split(" ")):
                return True
            elif val in iterable:
                return True
        return False


class E621API:
    BASE_URL = "https://e621.net/{endpoint}.json"

    def __init__(self, auth: Optional[Tuple[Username, ApiKey]] = None, timeout: int = 10) -> None:
        self.timeout = timeout
        self.session = SimpleSession(self.BASE_URL, timeout, auth)
        if auth is not None:
            self.username, self.api_key = auth
        else:
            self.username, self.api_key = None, None

        self.posts = endpoints.Posts(self)
        self.favorites = endpoints.Favorites(self)
        self.post_flags = endpoints.PostFlags(self)
        self.tags = endpoints.Tags(self)
        self.tag_aliases = endpoints.TagAliases(self)
        self.notes = endpoints.Notes(self)
        self.pools = endpoints.Pools(self)
        self.users = endpoints.Users(self)

    # ? This looks weird in an API class
    @cached_property
    def blacklist(self) -> BlackList:
        return BlackList(self.user.blacklisted_tags.split("\n"))

    @cached_property
    def user(self):
        if self.username is None or self.api_key is None:
            raise ValueError("Cannot access E621API.user for a non-authenticated user")
        return self.users.me
