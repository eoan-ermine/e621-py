from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Literal, Optional, Union

from ..models import EnrichedPool, Note, Tag, TagAlias
from .endpoints import BaseEndpoint


class PoolCategory(str, Enum):
    SERIES = "series"
    COLLECTION = "collection"


class TagCategory(IntEnum):
    GENERAL = 0
    ARTIST = 1
    COPYRIGHT = 3  # this is not a mistake. They really do skip number 2
    CHARACTER = 4
    SPECIES = 5
    INVALID = 6
    META = 7
    LORE = 8


PageNumber = int


class OffsetRelation(str, Enum):
    BEFORE = "b"
    AFTER = "a"


@dataclass
class PageOffset:
    relation: OffsetRelation
    id: int

    def __str__(self) -> str:
        return f"{self.relation}{self.id}"


class Tags(BaseEndpoint):
    def get(self, tag_id: int) -> Tag:
        return Tag(**self._api.session.get(f"tags/{tag_id}").json())

    def search(
        self,
        name_matches: Optional[str] = None,
        category: Optional[TagCategory] = None,
        order: Optional[Literal["date", "count", "name"]] = None,
        hide_empty: Optional[bool] = None,
        has_wiki: Optional[bool] = None,
        has_artist: Optional[bool] = None,
        limit: Optional[int] = None,
        page: Union[PageOffset, PageNumber, None] = None,
    ) -> List[Tag]:
        raw_tags = self._api.session.get(
            "tags",
            params={
                "search[name_matches]": name_matches,
                "search[category]": category,
                "search[order]": order,
                "search[hide_empty]": hide_empty,
                "search[has_wiki]": has_wiki,
                "search[has_artist]": has_artist,
                "limit": limit,
                "page": str(page) if isinstance(page, PageOffset) else page,
            },
        ).json()
        return [Tag(**tag) for tag in raw_tags] if isinstance(raw_tags, list) else []


class TagAliases(BaseEndpoint):
    def get(self, tag_alias_id: int) -> TagAlias:
        return TagAlias(**self._api.session.get(f"tag_aliases/{tag_alias_id}").json())

    def search(
        self,
        name_matches: Optional[str] = None,
        status: Optional[str] = None,
        order: Optional[Literal["status", "created_at", "updated_at", "name", "tag_count"]] = None,
        antecedent_tag_category: Optional[TagCategory] = None,
        consequent_tag_category: Optional[TagCategory] = None,
        limit: Optional[int] = None,
        page: Union[PageOffset, PageNumber, None] = None,
    ) -> List[TagAlias]:
        raw_tag_aliases = self._api.session.get(
            "tag_aliases",
            params={
                "search[name_matches]": name_matches,
                "search[status]": status,
                "search[order]": order,
                "search[antecedent_tag][category]": antecedent_tag_category,
                "search[consequent_tag][category]": consequent_tag_category,
                "limit": limit,
                "page": page,
            },
        ).json()
        return [TagAlias(**tag_alias) for tag_alias in raw_tag_aliases] if isinstance(raw_tag_aliases, list) else []


class Notes(BaseEndpoint):
    def get(self, note_id: int) -> Note:
        return Note(**self._api.session.get(f"notes/{note_id}").json())

    def search(
        self,
        body_matches: Optional[str] = None,
        post_id: Optional[int] = None,
        post_tags_match: Optional[str] = None,
        creator_name: Optional[str] = None,
        creator_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Note]:
        raw_notes = self._api.session.get(
            "notes",
            params={
                "search[body_matches]": body_matches,
                "search[post_id]": post_id,
                "search[post_tags_match]": post_tags_match,
                "search[creator_name]": creator_name,
                "search[creator_id]": creator_id,
                "search[is_active]": is_active,
                "limit": limit,
            },
        ).json()
        return [Note(**note) for note in raw_notes] if isinstance(raw_notes, list) else []

    def create(self, post_id: int, x: int, y: int, width: int, height: int, body: str) -> Note:
        return Note(
            **self._api.session.post(
                "notes",
                params={
                    "note[post_id]": post_id,
                    "note[x]": x,
                    "note[y]": y,
                    "note[width]": width,
                    "note[height]": height,
                    "note[body]": body,
                },
            ).json()
        )

    def update(self, note_id: int, post_id: int, x: int, y: int, width: int, height: int, body: str) -> Note:
        return Note(
            **self._api.session.put(
                f"notes/{note_id}",
                params={
                    "note[post_id]": post_id,
                    "note[x]": x,
                    "note[y]": y,
                    "note[width]": width,
                    "note[height]": height,
                    "note[body]": body,
                },
            ).json()
        )

    def delete(self, note_id: int) -> None:
        self._api.session.delete("notes/{note_id}")

    def revert(self, note_id: int, version_id: int) -> None:
        self._api.session.put(f"notes/{note_id}/revert", params={"version_id": version_id})


class Pools(BaseEndpoint):
    def get(self, pool_id: int) -> EnrichedPool:
        return EnrichedPool(**self._api.session.get(f"pools/{pool_id}").json())

    def search(
        self,
        name_matches: Optional[str] = None,
        id: Union[int, List[int], None] = None,
        description_matches: Optional[str] = None,
        creator_name: Optional[str] = None,
        creator_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        category: Optional[PoolCategory] = None,
        order: Optional[Literal["name", "created_at", "updated_at", "post_count"]] = None,
        limit: Optional[int] = None,
    ) -> List[EnrichedPool]:
        raw_pools = self._api.session.get(
            "pools",
            params={
                "search[name_matches]": name_matches,
                "search[id]": ",".join(map(str, id)) if isinstance(id, list) else id,
                "search[description_matches]": description_matches,
                "search[creator_name]": creator_name,
                "search[creator_id]": creator_id,
                "search[is_active]": is_active,
                "search[is_deleted]": is_deleted,
                "search[category]": category,
                "search[order]": order,
                "limit": limit,
            },
        ).json()
        return [EnrichedPool(**pool) for pool in raw_pools]

    def create(
        self, name: str, description: str, category: Optional[PoolCategory] = None, is_locked: Optional[bool] = None
    ) -> EnrichedPool:
        return EnrichedPool(
            **self._api.session.post(
                "pools",
                params={
                    "pool[name]": name,
                    "pool[description]": description,
                    "pool[category]": category,
                    "pool[is_locked]": is_locked,
                },
            ).json()
        )

    def update(
        self,
        pool_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        post_ids: Optional[List[int]] = None,
        is_active: Optional[bool] = None,
        category: Optional[PoolCategory] = None,
    ) -> EnrichedPool:
        return EnrichedPool(
            **self._api.session.put(
                f"pools/{pool_id}",
                params={
                    "pool[name]": name,
                    "pool[description]": description,
                    "pool[post_ids]": " ".join(map(str, post_ids)) if post_ids else post_ids,
                    "pool[is_active]": is_active,
                    "pool[category]": category,
                },
            ).json()
        )

    def revert(self, pool_id: int, version_id: int) -> None:
        self._api.session.put(f"pools/{pool_id}/revert", params={"version_id": version_id})
