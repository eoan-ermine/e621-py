from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import endpoints
from .models import EnrichedPool, EnrichedPost
from .session import SimpleSession, Username, ApiKey


class E621API:
    BASE_URL = "https://e621.net/{endpoint}.json"

    def __init__(
        self,
        auth: Optional[Tuple[Username, ApiKey]] = None,
        timeout: int = 10,
        blacklist: Iterable[str] = (),
        validate_input=True,
        validate_output=True,
    ) -> None:
        self.blacklist = set(l.strip() for l in blacklist)
        self.timeout = timeout
        self.session = SimpleSession(self.BASE_URL, timeout, auth)

        self.posts = endpoints.Posts(self)
        self.favorites = endpoints.Favorites(self)
        self.post_flags = endpoints.PostFlags(self)
        self.tags = endpoints.Tags(self)
        self.tag_aliases = endpoints.TagAliases(self)
        self.notes = endpoints.Notes(self)
        self.pools = endpoints.Pools(self)

    def get_pool(self, pool_id: int) -> EnrichedPool:
        return EnrichedPool(**self.session.get(f"pools/{pool_id}").json(), _e6api=self)
