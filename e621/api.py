from typing import Optional, Tuple

from . import endpoints
from .session import ApiKey, SimpleSession, Username


class E621:
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


class E926(E621):
    BASE_URL = "https://e926.net/{endpoint}.json"
