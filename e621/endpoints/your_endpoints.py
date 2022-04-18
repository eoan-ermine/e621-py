from io import BufferedReader
from pathlib import Path
from typing import Any, List, Optional, Union, overload

from backports.cached_property import cached_property
from typing_extensions import TypeAlias


from ..models import (
    Artist,
    ArtistVersion,
    AuthenticatedUser,
    Blip,
    BulkUpdateRequest,
    Post,
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
    ForumPost,
)
from ..enums import Rating
from .endpoints import BaseEndpoint, EmptySearcher


HttpUrl: TypeAlias = str
StringWithInlineDText: TypeAlias = str
UserID: TypeAlias = int
UserName: TypeAlias = str


class Posts(BaseEndpoint, generate=["update"]):
    _model = Post

    @overload
    def get(self, post_id: int) -> Post:
        pass

    @overload
    def get(self, post_id: List[int]) -> List[Post]:
        pass

    def get(self, post_id: Union[int, List[int]]) -> Union[Post, List[Post]]:
        if isinstance(post_id, int):
            return self._default_get(post_id)
        else:
            return self._default_search(
                {"tags": f"id:{','.join([str(id) for id in post_id])}"},
                limit=len(post_id),
                ignore_pagination=True,
            )

    def search(
        self,
        tags: Union[str, List[str]] = "",
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[Post]:
        if isinstance(tags, list):
            tags = " ".join(tags)
        posts = self._default_search({"tags": tags}, limit, page, ignore_pagination)
        # FIXME: this works if the person put the tag correctly, but doesn't work with tag aliases
        return [p for p in posts if not self._api.users.me.blacklist.intersects(p.all_tags)]

    def create(
        self,
        tag_string: Union[str, List[str]],
        file: Union[HttpUrl, Path, BufferedReader],
        rating: Rating,
        sources: List[HttpUrl],
        description: str,
        parent_id: Optional[int] = None,
        referer_url: Optional[HttpUrl] = None,
        md5_confirmation: Optional[str] = None,
        as_pending: bool = False,
    ) -> Post:
        if isinstance(tag_string, list):
            tag_string = " ".join(tag_string)
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
        ...


class Favorites(BaseEndpoint, generate=["delete"]):
    _model = Post
    _root_entity_name = "posts"

    def search(
        self,
        user_id: Optional[int] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[Post]:
        return self._default_search({"user_id": user_id}, limit, page, ignore_pagination)

    def create(self, post_id: int) -> Post:
        return self._default_create({"post_id": post_id})

    def delete(self, post_id: int) -> None:
        ...


class PostFlags(BaseEndpoint, generate=["search"]):
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
        ...

    def create(self, post_id: int, reason_name: str, parent_id: Optional[int] = None) -> PostFlag:
        if reason_name == "inferior" and parent_id is None:
            raise ValueError("parent_id is required for flags with 'inferior' reason")
        return self._magical_create(post_id, reason_name, parent_id)


class Users(BaseEndpoint, generate=["search", "get"]):
    _model = User

    @cached_property
    def me(self) -> AuthenticatedUser:
        if self._api.username is None or self._api.api_key is None:
            raise ValueError("Cannot access E621API.user for a non-authenticated user")
        return AuthenticatedUser.from_response(self._api.session.get(f"users/{self._api.username}"), self._api)

    def get(self, user_identifier: Union[UserID, UserName]) -> User:
        ...

    def search(
        self,
        name_matches: str,  # Wildcards supported
        level: Optional[Any] = None,
        min_level: Optional[Any] = None,
        max_level: Optional[Any] = None,
        can_upload_free: Optional[Any] = None,
        can_approve_posts: Optional[Any] = None,
        order: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[User]:
        ...


class PostVersions(BaseEndpoint, generate=["search"]):
    _model = PostVersion

    def search(
        self,
        updater_name: Optional[Any] = None,
        updater_id: Optional[Any] = None,
        post_id: Optional[Any] = None,
        reason: Optional[Any] = None,
        description: Optional[Any] = None,
        rating_changed: Optional[Any] = None,
        rating: Optional[Any] = None,
        parent_id: Optional[Any] = None,
        parent_id_changed: Optional[Any] = None,
        tags: Optional[Any] = None,
        tags_added: Optional[Any] = None,
        tags_removed: Optional[Any] = None,
        locked_tags: Optional[Any] = None,
        locked_tags_added: Optional[Any] = None,
        locked_tags_removed: Optional[Any] = None,
        source: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[PostVersion]:
        ...


class PostApprovals(BaseEndpoint, generate=["search"]):
    _model = PostApproval

    def search(
        self,
        user_name: str,
        post_tags_match: str,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[PostApproval]:
        ...


class NoteVersions(BaseEndpoint, generate=["search"]):
    _model = NoteVersion

    def search(
        self,
        body_matches: Optional[Any] = None,
        creator_name: Optional[Any] = None,
        post_tags_match: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[NoteVersion]:
        ...


class WikiPages(BaseEndpoint, generate=["search"]):
    _model = WikiPage

    def search(
        self,
        title: Optional[Any] = None,  # (Supports *)
        body_matches: Optional[Any] = None,
        creator_name: Optional[Any] = None,
        other_names_match: Optional[Any] = None,  # (Supports *)
        other_names_present: Optional[Any] = None,  # Yes/no
        hide_deleted: Optional[Any] = None,  # Yes/no
        order: Optional[Any] = None,  # title/time/post_count
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[WikiPage]:
        ...


# Only supports empty search
class WikiPageVersions(EmptySearcher[WikiPageVersion]):
    _model = WikiPageVersion


class Artists(BaseEndpoint, generate=["search"]):
    _model = Artist

    def search(
        self,
        any_name_matches: Optional[Any] = None,
        url_matches: Optional[Any] = None,
        creator_name: Optional[Any] = None,
        is_active: Optional[Any] = None,
        has_tag: Optional[Any] = None,
        is_linked: Optional[Any] = None,  # 0/1
        order: Optional[Any] = None,  # updated_at/name/created_at/post_count
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[Artist]:
        ...


class ArtistVersions(BaseEndpoint, generate=["search"]):
    _model = ArtistVersion

    def search(
        self,
        updater_name: Optional[Any] = None,
        name: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[ArtistVersion]:
        ...


class TagTypeVersions(BaseEndpoint, generate=["search"]):
    _model = TagTypeVersion

    def search(
        self,
        tag: Optional[Any] = None,
        user_name: Optional[Any] = None,
        user_id: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[TagTypeVersion]:
        ...


class TagImplications(BaseEndpoint, generate=["search"]):
    _model = TagImplication

    def search(
        self,
        name_matches: Optional[Any] = None,
        status: Optional[Any] = None,
        antecedent_tag_category: Optional[Any] = None,
        consequent_tag_category: Optional[Any] = None,
        order: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[TagImplication]:
        ...


class BulkUpdateRequests(BaseEndpoint, generate=["search"]):
    _model = BulkUpdateRequest

    def search(
        self,
        user_name: Optional[Any] = None,
        approver_name: Optional[Any] = None,
        title_matches: Optional[Any] = None,
        script_matches: Optional[Any] = None,
        status: Optional[Any] = None,
        order: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[BulkUpdateRequest]:
        ...


# Support CREATE/UPDATE/DELETE
class Blips(BaseEndpoint, generate=["search"]):
    _model = Blip

    def search(
        self,
        creator_name: Optional[Any] = None,
        body_matches: Optional[Any] = None,
        response_to: Optional[Any] = None,
        order: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[Blip]:
        ...


# Support CREATE
class Takedowns(BaseEndpoint, generate=["search"]):
    _model = Takedown

    def search(
        self,
        status: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[Takedown]:
        ...


class UserFeedbacks(BaseEndpoint, generate=["search"]):
    _model = UserFeedback

    def search(
        self,
        user_name: Optional[Any] = None,
        creator_name: Optional[Any] = None,
        body_matches: Optional[Any] = None,
        category: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[UserFeedback]:
        ...


# Only support empty searches. In case of parametrized search, returns forum_posts
class ForumTopics(EmptySearcher[ForumTopic]):
    _model = ForumTopic


class ForumPosts(BaseEndpoint, generate=["search"]):
    _model = ForumPost

    def search(
        self,
        topic_title_matches: Optional[Any] = None,
        body_matches: Optional[Any] = None,
        creator_name: Optional[Any] = None,
        topic_category_id: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[ForumPost]:
        ...


class PostSets(BaseEndpoint, generate=["search"]):
    _model = PostSet

    def search(
        self,
        name: Optional[Any] = None,
        shortname: Optional[Any] = None,
        creator_name: Optional[Any] = None,
        order: Optional[Any] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[PostSet]:
        ...
