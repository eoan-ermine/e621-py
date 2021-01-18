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

    @property
    def flag(self):
        return Flag(self._api)


class Tags:
    def __init__(self, api: e621):
        self._api = api

    def list(self, name_matches, page, category=None, order=None, hide_empty=None, has_wiki=None,
             has_artist=None, limit=None):
        return self._api.request(
            "tags",
            search={
                "name_matches": name_matches, "category": category, "order": order,
                "hide_empty": hide_empty, "has_wiki": has_wiki, "has_artists": has_artist,
            },
            limit=limit,
            page=page
        )


class TagAliases:
    def __init__(self, api: e621):
        self._api = api

    def list(self, name_matches, page, antecedent_tag_category, consequent_tag_category, status=None, order=None,
             limit=None):
        return self._api.request(
            "tag_aliases",
            search={
                "name_matches": name_matches, "status": status, "order": order,
                "antecedent_tag": {"category": antecedent_tag_category},
                "consequent_tag": {"category": consequent_tag_category},
            },
            limit=limit,
            page=page,
        )


class Notes:
    def __init__(self, api: e621):
        self._api = api

    def list(self, body_matches, post_id, post_tags_match, creator_name, creator_id, is_active, limit):
        return self._api.request(
            "notes",
            search={
                "body_matches": body_matches, "post_id": post_id, "post_tags_match": post_tags_match,
                "creator_name": creator_name, "creator_id": creator_id, "is_active": is_active
            },
            limit=limit,
        )

    def create(self, post_id, x, y, width, height, body):
        return self._api.request(
            "notes",
            note={
                "post_id": post_id, "x": x, "y": y, "width": width, "height": height,
                "body": body
            },
            type="POST"
        )

    def update(self, note_id, x, y, width, height, body):
        return self._api.request(
            f"notes/{note_id}",
            note={
                "x": x, "y": y, "width": width, "height": height, "body": body
            },
            type="PUT"
        )

    def delete(self, note_id):
        return self._api.request(
            f"notes/{note_id}",
            type="DELETE"
        )

    def revert(self, note_id, version_id):
        return self._api.request(
            f"notes/{note_id}/",
            version_id=version_id,
            type="PUT"
        )


class Pools:
    def __init__(self, api: e621):
        self._api = api

    def list(self, name_matches, is_active, is_deleted, category, limit,
             id=None, description_matches=None, creator_name=None, creator_id=None, order=None):

        if not all([id, description_matches, creator_name, creator_id]):
            raise RuntimeError("One of arguments should be passed: id, description_matches, creator_name,"
                               " creator_id")

        return self._api.request(
            "pools",
            search={
                "name_matches": name_matches, "id": id, "description_matches": description_matches, "creator_name":
                creator_name, "creator_id": creator_id, "is_active": is_active, "is_deleted": is_deleted, "category":
                category, "order": order
            },
            limit=limit
        )

    def create(self, name, description, category=None, is_locked=None):
        return self._api.request(
            "pools",
            pool={
                "name": name, "description": description, "category": category, "is_locked": is_locked
            },
            type="POST"
        )

    def update(self, pool_id, name=None, description=None, post_ids=None, is_active=None, category=None):
        return self._api.request(
            f"pools/{pool_id}",
            pool={
                "name": name, "description": description, "post_ids": post_ids, "is_active": is_active, "category":
                category
            },
            type="PUT"
        )

    def revert(self, pool_id, version_id):
        return self._api.request(
            f"pools/{pool_id}",
            version_id=version_id,
            type="PUT"
        )


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
        elif type == "PUT":
            return requests.put(
                url,
                params=kwargs,
                headers=HEADERS
            )

    @property
    def posts(self):
        return Posts(self)

    @property
    def tags(self):
        return Tags(self)

    @property
    def tag_aliases(self):
        return TagAliases(self)

    @property
    def notes(self):
        return Notes(self)

    @property
    def pools(self):
        return Pools(self)
