from io import BufferedReader
from pathlib import Path
from typing import List, Optional, Union

from backports.cached_property import cached_property
from typing_extensions import TypeAlias

from ..models import (
    Artist,
    ArtistVersion,
    AuthenticatedUser,
    Blip,
    BulkUpdateRequest,
    EnrichedPost,
    ForumTopic,
    NoteVersion,
    PostApproval,
    PostFlag,
    PostSet,
    PostVersion,
    TagImplication,
    TagTypeVersion,
    Takedown,
    User,
    UserFeedback,
    WikiPage,
    WikiPageVersion,
)
from ..util import StrEnum
from .endpoints import BaseEndpoint, Model


class Rating(StrEnum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


HttpUrl: TypeAlias = str
StringWithInlineDText: TypeAlias = str
UserID: TypeAlias = int
UserName: TypeAlias = str


class Posts(BaseEndpoint[EnrichedPost]):
    _model = EnrichedPost

    def get(self, post_id: int) -> EnrichedPost:
        return self._default_get(post_id)

    def search(
        self,
        tags: str = "",
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[EnrichedPost]:
        posts = self._default_search({"tags": tags}, limit, page, ignore_pagination)
        # FIXME: this works if the person put the tag correctly, but doesn't work with tag aliases
        return [p for p in posts if not self._api.users.me.blacklist.intersects(p.all_tags)]

    def create(
        self,
        tag_string: str,
        file: Union[HttpUrl, Path, BufferedReader],
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
            "upload[rating]": rating,
            "upload[sources]": ",".join(sources),
            "upload[description]": description,
            "upload[parent_id]": parent_id,
            "upload[referer_url]": referer_url,
            "upload[md5_confirmation]": md5_confirmation,
            "upload[as_pending]": as_pending,
        }
        files = {}
        openfile = None
        if isinstance(file, HttpUrl):
            params["upload[direct_url]"] = file
        elif isinstance(file, Path):
            files["upload[file]"] = openfile = file.open("rb")
        else:
            files["upload[file]"] = file
        try:
            r = self._api.session.post("posts", params=params, files=files)
            post = self.get(r.json()["post_id"])
            return post
        finally:
            if openfile is not None:
                openfile.close()

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
        self._default_update(
            post_id,
            params={
                "post[tag_string_diff]": tag_string_diff,
                "post[source_diff]": source_diff,
                "post[parent_id]": parent_id,
                "post[old_parent_id]": old_parent_id,
                "post[description]": description,
                "post[old_description]": old_description,
                "post[rating]": rating,
                "post[old_rating]": old_rating,
                "post[is_rating_locked]": is_rating_locked,
                "post[is_note_locked]": is_note_locked,
                "post[edit_reason]": edit_reason,
                "post[has_embedded_notes]": has_embedded_notes,
            },
        )


class Favorites(BaseEndpoint[EnrichedPost]):
    _model = EnrichedPost
    _root_entity_name = "posts"

    def search(
        self,
        user_id: Optional[int] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[EnrichedPost]:
        return self._default_search({"user_id": user_id}, limit, page, ignore_pagination)

    def create(self, post_id: int) -> EnrichedPost:
        return self._default_create({"post_id": post_id})

    def delete(self, post_id: int) -> None:
        self._default_delete(post_id)


class PostFlags(BaseEndpoint[PostFlag]):
    _model = PostFlag

    def search(
        self,
        post_id: Optional[int] = None,
        creator_id: Optional[int] = None,
        creator_name: Optional[str] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[PostFlag]:
        return self._default_search(
            {
                "search[post_id]": post_id,
                "search[creator_id]": creator_id,
                "search[creator_name]": creator_name,
            },
            limit,
            page,
            ignore_pagination,
        )

    def create(self, post_id: int, reason_name: str, parent_id: Optional[int] = None) -> PostFlag:
        if reason_name == "inferior" and parent_id is None:
            raise ValueError("parent_id is required for flags with 'inferior' reason")
        return self._default_create(
            {
                "post_flag[post_id]": post_id,
                "post_flag[reason_name]": reason_name,
                "post_flag[parent_id]": parent_id,
            }
        )


class EmptySearcher(BaseEndpoint[Model]):
    def search(self, limit: Optional[int] = None, page: int = 1, ignore_pagination: bool = False) -> List[Model]:
        return self._default_search({}, limit, page, ignore_pagination)


class Users(EmptySearcher[User]):
    _model = User

    @cached_property
    def me(self) -> AuthenticatedUser:
        if self._api.username is None or self._api.api_key is None:
            raise ValueError("Cannot access E621API.user for a non-authenticated user")
        return AuthenticatedUser.from_response(self._api.session.get(f"users/{self._api.username}"), self._api)

    def get(self, user_identifier: Union[UserID, UserName]) -> User:
        return self._default_get(user_identifier)


class PostVersions(EmptySearcher[PostVersion]):
    _model = PostVersion


class PostApprovals(EmptySearcher[PostApproval]):
    _model = PostApproval


class NoteVersions(EmptySearcher[NoteVersion]):
    _model = NoteVersion


class WikiPages(EmptySearcher[WikiPage]):
    _model = WikiPage


class WikiPageVersions(EmptySearcher[WikiPageVersion]):
    _model = WikiPageVersion


class Artists(EmptySearcher[Artist]):
    _model = Artist
    # search[any_name_matches]
    # search[url_matches]
    # search[creator_name]
    # search[is_active]
    # search[has_tag]
    # search[is_linked]=0/1
    # search[order]=updated_at/name/created_at/post_count


class ArtistVersions(EmptySearcher[ArtistVersion]):
    _model = ArtistVersion
    # search[updater_name]
    # search[name]


class TagTypeVersions(EmptySearcher[TagTypeVersion]):
    _model = TagTypeVersion
    # search[tag]
    # search[user_name]
    # search[user_id]


class TagImplications(EmptySearcher[TagImplication]):
    _model = TagImplication


class BulkUpdateRequests(EmptySearcher[BulkUpdateRequest]):
    _model = BulkUpdateRequest


class Blips(EmptySearcher[Blip]):
    _model = Blip


class Takedowns(EmptySearcher[Takedown]):
    _model = Takedown


class UserFeedbacks(EmptySearcher[UserFeedback]):
    _model = UserFeedback


class ForumTopics(EmptySearcher[ForumTopic]):
    _model = ForumTopic


class PostSets(EmptySearcher[PostSet]):
    _model = PostSet
