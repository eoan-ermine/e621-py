# This file has been automagically generated by our scripts
# Please, do not edit it by hand because all of your changes
# will inevitably be overwritten. Edit models.py instead.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base_model import BaseModel

__all__ = (
    "File",
    "Preview",
    "Field720p",
    "Field480p",
    "Original",
    "Alternates",
    "Sample",
    "Score",
    "Tags",
    "Flags",
    "Relationships",
    "Post",
    "Posts",
    "PostFlag",
    "Tag",
    "TagAlias",
    "Note",
    "Pool",
)


class File(BaseModel):
    width: int
    height: int
    ext: str
    size: int
    md5: str
    url: str


class Preview(BaseModel):
    width: int
    height: int
    url: str


class Field720p(BaseModel):
    type: str
    height: int
    width: int
    urls: List[str]


class Field480p(Field720p):
    pass


class Original(BaseModel):
    type: str
    height: int
    width: int
    urls: List[Optional[str]]


class Alternates(BaseModel):
    field_720p: Optional[Field720p] = Field(None, alias="720p")
    field_480p: Optional[Field480p] = Field(None, alias="480p")
    original: Optional[Original] = None


class Sample(BaseModel):
    has: bool
    height: int
    width: int
    url: str
    alternates: Alternates


class Score(BaseModel):
    up: int
    down: int
    total: int


class Tags(BaseModel):
    general: List[str]
    species: List[str]
    character: List[str]
    copyright: List[str]
    artist: List[str]
    invalid: List[str]
    lore: List[str]
    meta: List[str]


class Flags(BaseModel):
    pending: bool
    flagged: bool
    note_locked: bool
    status_locked: bool
    rating_locked: bool
    deleted: bool


class Relationships(BaseModel):
    parent_id: Optional[int]
    has_children: bool
    has_active_children: bool
    children: List[int]


class Post(BaseModel):
    id: int
    created_at: str
    updated_at: str
    file: File
    preview: Preview
    sample: Sample
    score: Score
    tags: Tags
    locked_tags: List[str]
    change_seq: int
    flags: Flags
    rating: str
    fav_count: int
    sources: List[str]
    pools: List[int]
    relationships: Relationships
    approver_id: Optional[int]
    uploader_id: int
    description: str
    comment_count: int
    is_favorited: bool
    has_notes: bool
    duration: Optional[float]


class Posts(BaseModel):
    posts: List[Post]


class PostFlag(BaseModel):
    id: int
    created_at: str
    post_id: int
    reason: str
    creator_id: Optional[int] = None
    is_resolved: bool
    updated_at: str
    is_deletion: bool
    category: str


class Tag(BaseModel):
    id: int
    name: str
    post_count: int
    related_tags: str
    related_tags_updated_at: str
    category: int
    is_locked: bool
    created_at: str
    updated_at: str


class TagAlias(BaseModel):
    id: int
    antecedent_name: str
    reason: str
    creator_id: int
    created_at: str
    forum_post_id: Optional[int]
    updated_at: Optional[str]
    forum_topic_id: Optional[int]
    consequent_name: str
    status: str
    post_count: int
    approver_id: Optional[int]


class Note(BaseModel):
    id: int
    created_at: str
    updated_at: str
    creator_id: int
    x: int
    y: int
    width: int
    height: int
    version: int
    is_active: bool
    post_id: int
    body: str
    creator_name: str


class Pool(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str
    creator_id: int
    description: str
    is_active: bool
    category: str
    is_deleted: bool
    post_ids: List[int]
    creator_name: str
    post_count: int
