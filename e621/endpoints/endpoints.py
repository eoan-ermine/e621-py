from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api import E621API


@dataclass
class BaseEndpoint:
    _api: "E621API"
