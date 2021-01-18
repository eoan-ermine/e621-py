import requests

import e621

API_ENDPOINT = "https://e621.net/"
USER_AGENT = "e621-py/0.1.0 (by Eoan_Ermine on e621)"

HEADERS = {"user-agent": USER_AGENT}


def get_url(method: str) -> str:
    return API_ENDPOINT + method + ".json"


class Flag:
    def __init__(self, api: e621):
        self._api = api

    def list(self, post_id, creator_id, creator_name):
        return self._api.request(
            "post_flags",
            search={
                "post_id": post_id, "creator_id": creator_id, "creator_name": creator_name
            }
        )

    def create(self, post_id, reason_name, parent_id=None):
        return self._api.request(
            "post_flags",
            post_flags={
                "post_id": post_id, "reason_name": reason_name, "parent_id": parent_id
            },
            type="POST"
        )


class Posts:
    def __init__(self, api: e621):
        self._api = api

    def create(self, tag_string, file, rating, source, direct_url=None, description=None, parent_id=None,
               referer_url=None, md5_confirmation=None, as_pending=None):
        return self._api.request(
            "uploads",
            upload={
                "tag_string": tag_string, "file": file, "rating": rating, "source": source,
                "direct_url": direct_url, "description": description, "parent_id": parent_id,
                "referer_url": referer_url, "md5_confirmation": md5_confirmation, "as_pending": as_pending
            },
            type="POST"
        )

    def update(self, post_id: int, tag_string_diff=None, source_diff=None, parent_id=None, old_parent_id=None,
               description=None, old_description=None, rating=None, old_rating=None, is_rating_locked=None,
               is_note_locked=None, edit_reason=None, has_embedded_notes=None):
        return self._api.request(
            f"posts/{post_id}",
            post={
                "tag_string_diff": tag_string_diff, "source_diff": source_diff, "parent_id": parent_id,
                "old_parent_id": old_parent_id, "description": description, "old_description": old_description,
                "rating": rating, "old_rating": old_rating, "is_rating_locked": is_rating_locked,
                "is_note_locked": is_note_locked, "edit_reason": edit_reason, "has_embedded_notes": has_embedded_notes
            },
            type="PATCH"
        )

    def list(self, limit: int, tags: str, page: int):
        return self._api.request(
            "posts", limit=limit, tags=tags, page=page
        )

    def vote(self, post_id, score, no_unvote=None):
        return self._api.request(
            f"posts/{post_id}/votes", score=score, no_unvote=no_unvote,
            type="POST"
        )

    def flag(self):
        return Flag(self._api)


class e621:
    def __init__(self, login: str, api_key: str):
        self._login = login
        self._api_key = api_key

        self._credentials = {
            "login": login, "api_key": api_key
        }

    def request(self, method: str, type="GET", **kwargs):
        url = get_url(method)
        kwargs.update(self._credentials)

        if type == "GET":
            return requests.get(
                url,
                params=kwargs,
                headers=HEADERS
            ).json()
        elif type == "POST":
            return requests.post(
                url,
                params=kwargs,
                headers=HEADERS
            ).json()
        elif type == "PATCH":
            return requests.patch(
                url,
                params=kwargs,
                headers=HEADERS
            ).json()

    def posts(self):
        return Posts(self)