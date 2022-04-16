from typing import Any, Dict, List, Optional, Tuple

import requests
from typing_extensions import TypeAlias

Username: TypeAlias = str
ApiKey: TypeAlias = str


class SimpleSession(requests.Session):
    """A session that automatically configures itself with the necessary auth and headers
    and always makes requests to base_url
    """

    def __init__(self, base_url: str, timeout: int, auth: Optional[Tuple[Username, ApiKey]] = None) -> None:
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout
        self.headers.update({"User-Agent": "e621-py (by Eoan Ermine)"})
        if auth is not None:
            self.auth = auth

    def request(self, method: str, endpoint: str, *args: Any, **kwargs: Any) -> requests.Response:
        url = self.base_url.format(endpoint=endpoint)
        r = super().request(method, url, *args, timeout=self.timeout, **kwargs)
        r.raise_for_status()
        return r

    def paginated_get(
        self,
        endpoint: str,
        params: Dict[str, Any],
        root_entity_name: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> List[Dict[Any, Any]]:
        """Performs a paginated GET request to the given endpoint, returning a list of all the results"""
        results: List[Dict[Any, Any]] = []
        while True:
            json = self.get(endpoint, params, *args, **kwargs).json()
            chunk: List[Dict[Any, Any]]
            if root_entity_name is not None and isinstance(json, dict):
                chunk = json[root_entity_name]
            else:
                chunk = json
            params["page"] += 1
            params["limit"] -= len(chunk)
            results.extend(chunk)
            if params["limit"] <= 0:
                break
        return results
