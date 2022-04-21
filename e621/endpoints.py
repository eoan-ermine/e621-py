import functools
import inspect
from dataclasses import dataclass
from io import BufferedReader
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

from backports.cached_property import cached_property
from typing_extensions import Literal, ParamSpec, TypeAlias

from e621.util import camel_to_snake

from .base_model import BaseModel
from .enums import OffsetRelation, PoolCategory, Rating, TagCategory
from .models import (
    Artist,
    ArtistVersion,
    AuthenticatedUser,
    Blip,
    BulkUpdateRequest,
    ForumPost,
    ForumTopic,
    Note,
    NoteVersion,
    Pool,
    Post,
    PostApproval,
    PostFlag,
    PostSet,
    PostVersion,
    Tag,
    TagAlias,
    TagImplication,
    TagTypeVersion,
    Takedown,
    User,
    UserFeedback,
    WikiPage,
    WikiPageVersion,
)

if TYPE_CHECKING:
    from .api import E621


HttpUrl: TypeAlias = str
StringWithInlineDText: TypeAlias = str
UserID: TypeAlias = int
UserName: TypeAlias = str
Model = TypeVar("Model", bound=BaseModel)
PageNumber = int


@dataclass
class PageOffset:
    relation: OffsetRelation
    id: int

    def __str__(self) -> str:
        return f"{self.relation}{self.id}"


_METHOD_MAPPER = {
    "create": "_magical_create",
    "get": "_default_get",
    "search": "_magical_search",
    "update": "_magical_update",
    "delete": "_default_delete",
}


class BaseEndpoint(Generic[Model]):
    _model: Type[Model]
    _root_entity_name: str
    _url: str
    _model_snake_case_name: str

    def __init__(self, api: "E621") -> None:
        self._api = api

    def __init_subclass__(cls, *, generate=()) -> None:
        super().__init_subclass__()
        class_name_in_snake_case = camel_to_snake(cls.__name__)
        if getattr(cls, "_root_entity_name", None) is None:
            cls._root_entity_name = class_name_in_snake_case
        if getattr(cls, "_url", None) is None:
            cls._url = class_name_in_snake_case
        cls._model_snake_case_name = camel_to_snake(cls._model.__name__)
        for method_name in generate:
            setattr(cls, method_name, _generate_endpoint_method(cls, getattr(cls, method_name)))

    def _default_get(self, identifier: Any, **kwargs: Any) -> Model:
        return self._model.from_response(self._api.session.get(f"{self._url}/{identifier}", **kwargs), self._api)

    def _default_search(
        self, params: Dict[str, Any], limit: Optional[int], page: int = 1, ignore_pagination=False
    ) -> List[Model]:
        # In case the user reuses the same set of params
        params = params.copy()
        params.update({"limit": limit, "page": page})
        if ignore_pagination:
            if limit is None:
                raise ValueError("limit is required when ignore_pagination is True")
            return self._model.from_list(
                self._api.session.paginated_get(self._url, params, self._root_entity_name), self._api
            )
        else:
            return self._model.from_response(self._api.session.get(self._url, params=params), self._api, expect=list)

    def _default_create(self, params: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Model:
        return self._model.from_response(self._api.session.post(self._url, params=params, files=files), self._api)

    def _default_update(self, identifier: Union[str, int], params: Dict[str, Any]) -> None:
        self._api.session.patch(f"{self._url}/{identifier}", params=params)

    def _default_delete(self, identifier: Union[str, int], **kwargs: Any) -> None:
        self._api.session.delete(f"{self._url}/{identifier}", **kwargs)

    def _magical_search(self, *raw_args: Any, _param_prefix="search") -> List[Model]:
        """A default search that automatically generates search params from self.search definition"""
        *args, limit, page, ignore_pagination = raw_args
        return self._magical_method(
            self.search, self._default_search, _param_prefix, (), (limit, page, ignore_pagination), args
        )

    def _magical_create(self, *args: Any, _param_prefix=None) -> Model:
        """A default create that automatically generates create params from self.create definition"""
        if _param_prefix is None:
            _param_prefix = self._model_snake_case_name
        return self._magical_method(self.create, self._default_create, _param_prefix, (), (), args)

    def _magical_update(self, identifier: Union[str, int], *args: Any, _param_prefix=None) -> Model:
        if _param_prefix is None:
            _param_prefix = self._model_snake_case_name
        return self._magical_method(self.update, self._default_update, _param_prefix, (identifier,), (), args, 1)

    def _magical_method(
        self,
        method: Callable,
        default_method: Callable,
        param_prefix: str,
        before_meta_args: Sequence[Any],
        after_meta_args: Sequence[Any],
        args: Any,
        arg_offset: int = 0,
    ) -> Any:
        parameters = list(inspect.signature(method).parameters)
        return default_method(
            *before_meta_args,
            {f"{param_prefix}[{argname}]": arg for argname, arg in zip(parameters[arg_offset:], args)},
            *after_meta_args,
        )


class EmptySearcher(BaseEndpoint[Model]):
    _model = BaseModel

    def search(self, limit: Optional[int] = None, page: int = 1, ignore_pagination: bool = False) -> List[Model]:
        return self._default_search({}, limit, page, ignore_pagination)


_P = ParamSpec("_P")
_T = TypeVar("_T")


def _generate_endpoint_method(cls: Type[BaseEndpoint], method: Callable[_P, _T]) -> Callable[_P, _T]:
    magical_method = getattr(cls, _METHOD_MAPPER[method.__name__])
    method_signature = inspect.signature(method)

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        bound_signature = method_signature.bind(self, *args, **kwargs)
        bound_signature.apply_defaults()
        return magical_method(*bound_signature.arguments.values())

    return wrapper  # type: ignore


class Posts(BaseEndpoint[Post], generate=["update"]):
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
        if self._api.logged_in:
            # FIXME: this works if the person put the tag correctly, but doesn't work with tag aliases
            return [p for p in posts if not self._api.users.me.blacklist.intersects(p.all_tags)]
        else:
            return posts

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


class Favorites(BaseEndpoint[Post], generate=["delete"]):
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


class Pools(BaseEndpoint[Pool], generate=["get", "create"]):
    _model = Pool

    def get(self, pool_id: int) -> Pool:
        ...

    def search(
        self,
        name_matches: Optional[str] = None,
        id: Union[int, List[int], str, None] = None,
        description_matches: Optional[str] = None,
        creator_name: Optional[str] = None,
        creator_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        category: Optional[PoolCategory] = None,
        order: Optional[Literal["name", "created_at", "updated_at", "post_count"]] = None,
        limit: Optional[int] = None,
        page: int = 1,
        ignore_pagination: bool = False,
    ) -> List[Pool]:
        if isinstance(id, list):
            id = ",".join(map(str, id))

        return self._magical_search(
            name_matches,
            id,
            description_matches,
            creator_name,
            creator_id,
            is_active,
            is_deleted,
            category,
            order,
            limit,
            page,
            ignore_pagination,
        )

    def create(
        self,
        name: str,
        description: str,
        category: Optional[PoolCategory] = None,
        is_locked: Optional[bool] = None,
    ) -> Pool:
        ...

    def update(
        self,
        pool_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        post_ids: Union[List[int], str, None] = None,
        is_active: Optional[bool] = None,
        category: Optional[PoolCategory] = None,
    ) -> Pool:
        if isinstance(post_ids, list):
            post_ids = " ".join(map(str, post_ids))
        return self._magical_update(pool_id, name, description, post_ids, is_active, category)

    def revert(self, pool_id: int, version_id: int) -> None:
        self._api.session.put(f"pools/{pool_id}/revert", params={"version_id": version_id})


class Tags(BaseEndpoint[Tag], generate=["get", "search"]):
    _model = Tag

    def get(self, tag_id: int) -> Tag:
        ...

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
        ignore_pagination: bool = False,
    ) -> List[Tag]:
        ...


class TagAliases(BaseEndpoint[TagAlias], generate=["get"]):
    _model = TagAlias

    def get(self, tag_alias_id: int) -> TagAlias:
        ...

    def search(
        self,
        name_matches: Optional[str] = None,
        status: Optional[str] = None,
        order: Optional[Literal["status", "created_at", "updated_at", "name", "tag_count"]] = None,
        antecedent_tag_category: Optional[TagCategory] = None,
        consequent_tag_category: Optional[TagCategory] = None,
        limit: Optional[int] = None,
        page: Union[PageOffset, PageNumber] = 1,
        ignore_pagination: bool = False,
    ) -> List[TagAlias]:
        return self._default_search(
            {
                "search[name_matches]": name_matches,
                "search[status]": status,
                "search[order]": order,
                "search[antecedent_tag][category]": antecedent_tag_category,
                "search[consequent_tag][category]": consequent_tag_category,
            },
            limit,
            page,
            ignore_pagination,
        )


class Notes(BaseEndpoint[Note], generate=["get", "search", "create", "update", "delete"]):
    _model = Note

    def get(self, note_id: int) -> Note:
        ...

    def search(
        self,
        body_matches: Optional[str] = None,
        post_id: Optional[int] = None,
        post_tags_match: Optional[str] = None,
        creator_name: Optional[str] = None,
        creator_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: Optional[int] = None,
        ignore_pagination: bool = False,
    ) -> List[Note]:
        ...

    def create(self, post_id: int, x: int, y: int, width: int, height: int, body: str) -> Note:
        ...

    def update(self, note_id: int, post_id: int, x: int, y: int, width: int, height: int, body: str) -> None:
        ...

    def delete(self, note_id: int) -> None:
        ...

    def revert(self, note_id: int, version_id: int) -> None:
        self._api.session.put(f"notes/{note_id}/revert", params={"version_id": version_id})


class PostFlags(BaseEndpoint[PostFlag], generate=["search"]):
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


class Users(BaseEndpoint[User], generate=["search", "get"]):
    _model = User

    @cached_property
    def me(self) -> AuthenticatedUser:
        if not self._api.logged_in:
            raise ValueError("Cannot access Users.me for a non-authenticated user")
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


class PostVersions(BaseEndpoint[PostVersion], generate=["search"]):
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
