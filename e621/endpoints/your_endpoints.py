from enum import Enum
from io import FileIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Optional, Union

from typing_extensions import TypeAlias

from ..models import AuthenticatedUser, EnrichedPost, PostFlag, User
from .endpoints import BaseEndpoint

if TYPE_CHECKING:
    from ..api import E621API


class Rating(Enum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


HttpUrl: TypeAlias = str
StringWithInlineDText: TypeAlias = str
UserID: TypeAlias = int
UserName: TypeAlias = str


class Posts(BaseEndpoint):
    def get(self, post_id: int) -> EnrichedPost:
        return EnrichedPost.from_response(self._api.session.get(f"posts/{post_id}"))

    def list(
        self,
        tags: str = "",
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[EnrichedPost]:
        return _list_posts(self._api, "posts", {"tags": tags, "limit": limit, "page": page}, ignore_pagination)

    def create(
        self,
        tag_string: str,
        file: Union[Path, FileIO, HttpUrl],
        rating: Rating,
        sources: List[HttpUrl],
        description: str,
        parent_id: Optional[int] = None,
        referer_url: Optional[HttpUrl] = None,
        md5_confirmation: Optional[str] = None,
        as_pending: bool = False,
    ) -> EnrichedPost:
        params = {
            "upload[tag_string]": tag_string,
            "upload[rating]": rating.value,
            "upload[sources]": ",".join(sources),
            "upload[description]": description,
            "upload[parent_id]": parent_id,
            "upload[referer_url]": referer_url,
            "upload[md5_confirmation]": md5_confirmation,
            "upload[as_pending]": as_pending,
        }
        files = {}
        if isinstance(file, Path):
            files["upload[file]"] = file.open("rb")
        elif isinstance(file, BinaryIO):
            files["upload[file]"] = file
        elif isinstance(file, HttpUrl):
            params["upload[direct_url]"] = file
        r = self._api.session.post("posts", params=params, files=files)

        return self.get(r.json()["post_id"])

    def update(
        self,
        post_id: int,
        tag_string_diff: Optional[str] = None,
        source_diff: Optional[str] = None,
        parent_id: Optional[int] = None,
        old_parent_id: Optional[int] = None,
        description: Optional[str] = None,
        old_description: Optional[str] = None,
        rating: Optional[Rating] = None,
        old_rating: Optional[Rating] = None,
        is_rating_locked: Optional[bool] = None,
        is_note_locked: Optional[bool] = None,
        edit_reason: Optional[StringWithInlineDText] = None,
        has_embedded_notes: Optional[bool] = None,
    ) -> None:
        # Two simple if-statements would be enough but pylance is picky so
        # we resort to this method for full typehint support.
        normalized_rating = rating if rating is None else rating.value
        normalized_old_rating = old_rating if old_rating is None else old_rating.value
        self._api.session.patch(
            f"posts/{post_id}",
            params={
                "post[tag_string_diff]": tag_string_diff,
                "post[source_diff]": source_diff,
                "post[parent_id]": parent_id,
                "post[old_parent_id]": old_parent_id,
                "post[description]": description,
                "post[old_description]": old_description,
                "post[rating]": normalized_rating,
                "post[old_rating]": normalized_old_rating,
                "post[is_rating_locked]": is_rating_locked,
                "post[is_note_locked]": is_note_locked,
                "post[edit_reason]": edit_reason,
                "post[has_embedded_notes]": has_embedded_notes,
            },
        )


class Favorites(BaseEndpoint):
    def list(self, user_id: Optional[int] = None, limit: Optional[int] = None, page: int = 1) -> List[EnrichedPost]:
        return _list_posts(self._api, "favorites", {"user_id": user_id, "limit": limit, "page": page})

    def create(self, post_id: int) -> EnrichedPost:
        return EnrichedPost.from_response(self._api.session.post("favorites", params={"post_id": post_id}))

    def delete(self, post_id: int) -> None:
        self._api.session.delete(f"favorites/{post_id}")


class PostFlags(BaseEndpoint):
    def list(
        self,
        post_id: Optional[int] = None,
        creator_id: Optional[int] = None,
        creator_name: Optional[str] = None,
    ) -> List[PostFlag]:
        params = {
            "search[post_id]": post_id,
            "search[creator_id]": creator_id,
            "search[creator_name]": creator_name,
        }
        return PostFlag.from_response(self._api.session.get("post_flags", params=params), expect=list)

    def create(self, post_id: int, reason_name: str, parent_id: Optional[int] = None) -> PostFlag:
        if reason_name == "inferior" and parent_id is None:
            raise ValueError
        params = {
            "post_flag[post_id]": post_id,
            "post_flag[reason_name]": reason_name,
            "post_flag[parent_id]": parent_id,
        }
        return PostFlag.from_response(self._api.session.post("post_flags", params=params))


class Users(BaseEndpoint):
    @property
    def me(self) -> AuthenticatedUser:
        return AuthenticatedUser.from_response(self._api.session.get(f"users/{self._api.username}"))

    def get(self, user_identifier: Union[UserID, UserName]) -> User:
        return User.from_response(self._api.session.get(f"users/{user_identifier}"))

    def list(self, limit: Optional[int] = None, page: int = 1) -> List[User]:
        return User.from_response(self._api.session.get("users", params={"limit": limit, "page": page}), expect=list)


def _list_posts(
    api: "E621API",
    endpoint_name: str,
    params: Dict[str, Any],
    ignore_pagination: bool = False,
) -> List[EnrichedPost]:
    if ignore_pagination:
        posts = EnrichedPost.from_list(api.session.paginated_get(endpoint_name, params, root_entity_name="posts"))
    else:
        posts = EnrichedPost.from_response(api.session.get(endpoint_name, params=params), expect=list)
    # FIXME: this works with single tag on the blacklist but e621 supports tag groups in blacklists
    # FIXME: this works if the person put the tag correctly, but doesn't work with tag aliases
    return [p for p in posts if not api.blacklist.intersects(p.all_tags)]
