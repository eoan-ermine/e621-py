import enum


class StrEnum(str, enum.Enum):
    pass


class Rating(StrEnum):
    EXPLICIT = "e"
    SAFE = "s"
    QUESTIONABLE = "q"


print(Rating.QUESTIONABLE, str(Rating.QUESTIONABLE))
