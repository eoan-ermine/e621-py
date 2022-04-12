from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from typing_extensions import TypeAlias

from . import endpoints
from .models import EnrichedPool, EnrichedPost

Username: TypeAlias = str
ApiKey: TypeAlias = str


class SimpleSession(requests.Session):
    """A session that automatically configures itself with the necessary auth and headers
    and always makes requests to base_url
    """

    def __init__(self, base_url: str, timeout: int, auth: Optional[Tuple[Username, ApiKey]] = None):
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout
        self.headers.update({"User-Agent": "e621-py (by Eoan Ermine)"})
        if auth is not None:
            self.auth = auth

    def request(self, method: str, endpoint: str, *args: Any, **kwargs: Any) -> requests.Response:
        url = self.base_url.format(endpoint=endpoint)
        r = super().request(method, url, *args, timeout=self.timeout, **kwargs)
        r.raise_for_status()
        return r


class E621API:
    BASE_URL = "https://e621.net/{endpoint}.json"

    def __init__(
        self,
        auth: Optional[Tuple[Username, ApiKey]] = None,
        timeout: int = 10,
        blacklist: Iterable[str] = (),
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

    # Deprecated code. Will be replaced by endpoint classes soon

    def get_posts(self, tags: str, post_count: int = 100000) -> List[EnrichedPost]:
        params = {"tags": tags, "limit": post_count, "page": 1}
        all_raw_posts: list[dict[str, Any]] = []
        # TODO: Replace me with walrus when it's available :(
        raw_posts = self.session.get("posts", params).json()["posts"]
        while len(raw_posts) and post_count - len(raw_posts) >= 0:
            params["page"] += 1
            params["limit"] -= len(raw_posts)
            all_raw_posts.extend(raw_posts)
            # TODO: Replace me with walrus when it's available :(
            raw_posts = self.session.get("posts", params).json()["posts"]
        posts = (EnrichedPost(**p) for p in all_raw_posts)
        # FIXME: this works with single tag on the blacklist but e621 supports tag groups in blacklists
        # FIXME: this works if the person put the tag correctly, but doesn't work with tag aliases
        return [p for p in posts if not p.all_tags & self.blacklist]

    def get_post(self, post_id: int) -> EnrichedPost:
        return EnrichedPost(**self.session.get(f"posts/{post_id}").json())

    def get_pool(self, pool_id: int) -> EnrichedPool:
        return EnrichedPool(**self.session.get(f"pools/{pool_id}").json(), _e6api=self)
