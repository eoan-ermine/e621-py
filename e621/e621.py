import requests

API_ENDPOINT = "https://e621.net/"
USER_AGENT = "e621-py/0.1.0 (by Eoan_Ermine on e621)"

HEADERS = {"user-agent": USER_AGENT}


def get_url(method: str) -> str:
	return API_ENDPOINT + method + ".json"


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
	
	def list(self, limit: int, tags: str, page: int):
		return self.request(
			"posts", limit=limit, tags=tags, page=page
		)
		
	def post_flags_list(self, post_id: int, creator_id: int, creator_name: str):
		return self.request(
			"post_flags", search={
				"post_id": post_id,
				"creator_id": creator_id,
				"creator_name": creator_name
			}
		)
	
	def post_flags_create(self, post_id, reason_name, parent_id=None):
		return self.requests(
			"post_flags", post_flag={
				"post_id": post_id,
				"reason_name": reason_name,
				"parent_id": parent_id
			}, type="POST"
		)
	
	def vote(self, id, score, no_unvote):
		return self.requests(
			f"posts/{id}/votes",
			score=score, no_unvote=no_unvote, type="POST"
		)

