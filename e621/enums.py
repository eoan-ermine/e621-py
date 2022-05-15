import enum

__all__ = ["Rating"]


class StrEnum(str, enum.Enum):
    pass


class Rating(StrEnum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


class PoolCategory(StrEnum):
    SERIES = "series"
    COLLECTION = "collection"


class TagCategory(enum.IntEnum):
    GENERAL = 0
    ARTIST = 1
    COPYRIGHT = 3  # this is not a mistake. They really do skip number 2
    CHARACTER = 4
    SPECIES = 5
    INVALID = 6
    META = 7
    LORE = 8


class OffsetRelation(StrEnum):
    BEFORE = "b"
    AFTER = "a"
