from typing import List, Optional

from e621.models import Note, Pool

from .endpoints import BaseEndpoint


class Tags(BaseEndpoint):
    pass


class TagAliases(BaseEndpoint):
    pass


class Notes(BaseEndpoint):
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
        raw_notes = self._api.session.request(
            "GET",
            "notes.json",
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
        return [Note(**note) for note in raw_notes]

    def create(self, post_id: int, x: int, y: int, width: int, height: int, body: str) -> Note:
        return Note(
            **self._api.session.request(
                "POST",
                "notes.json",
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

    def update(self, note_id: int, x: int, y: int, width: int, height: int, body: str) -> Note:
        return Note(
            **self._api.session.request(
                "PUT",
                f"notes/{note_id}.json",
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
        self._api.session.request("POST", f"notes/{note_id}.json")

    def revert(self, version_id) -> None:
        self._api.session.request("PUT", f"notes/{note_id}/revert.json", params={"version_id": version_id})


class Pools(BaseEndpoint):
    def search(
        self,
        name_matches: Optional[str] = None,
        id: Optional[int] = None,
        description_matches: Optional[str] = None,
        creator_name: Optional[str] = None,
        creator_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        category: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Pool]:
        raw_pools = self._api.session.request(
            "GET",
            "pools.json",
            params={
                "search[name_matches]": name_matches,
                "search[id]": id,
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
        return [Pool(**pool) for pool in raw_pools]

    def create(
        self, name: str, description: str, category: Optional[str] = None, is_locked: Optional[bool] = None
    ) -> Pool:
        return Pool(
            **self._api.session.request(
                "POST",
                "pools.json",
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
        category: Optional[str] = None,
    ) -> Pool:
        return Pool(
            **self._api.session.request(
                "PUT",
                f"pools/{pool_id}.json",
                params={
                    "pool[name]": name,
                    "pool[description]": description,
                    "pool[post_ids]": " ".join(map(str, post_ids)),
                    "pool[is_active]": is_active,
                    "pool[category]": category,
                },
            ).json()
        )

    def revert(self, pool_id: int, version_id: int) -> None:
        self._api.session.request("PUT", f"pools/{pool_id}/revert.json", params={"version_id": version_id})
