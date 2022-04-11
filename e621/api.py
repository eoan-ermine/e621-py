from __future__ import annotations

import requests


class APIRequest:
    def __init__(self, method, params):
        self.method = method
        self.params = params


class Endpoint:
    def __init__(self, api):
        self._api = api


class PostsEndpoint(Endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FavoritesEndpoint(Endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NotesEndpoint(Endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PoolsEndpoint(Endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RootEndpoint(Endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def posts(self):
        return PostsEndpoint(self._api)

    @property
    def favorites(self):
        return FavoritesEndpoint(self._api)

    @property
    def notes(self):
        return NotesEndpoint(self._api)

    @property
    def pools(self):
        return PoolsEndpoint(self._api)


class API:
    API_URL = "https://e621.net/{endpoint}.json"

    def __new__(cls, *args, **kwargs):
        api = object.__new__(cls)
        api.__init__(*args, **kwargs)

        return RootEndpoint(api)

    def __init__(self, login: str | None = None, api_key: str | None = None, timeout = 10):
        self.login, self.api_key = login, api_key
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers = {"User-Agent": "e621-py (by Eoan Ermine)"}

    def send(self, request, http_method: str):
        request.params["login"] = self.login
        request.params["api_key"] = self.api_key

        method_url = self.API_URL.format(endpoint=request.method)
        response = self.session.request(
            http_method, method_url, params = request.params, timeout = self.timeout
        )

        return response.json()
