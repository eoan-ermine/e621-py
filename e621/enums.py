import enum

__all__ = ["Rating"]


class StrEnum(str, enum.Enum):
    pass


class Rating(StrEnum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"
