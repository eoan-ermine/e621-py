# e621
e621 is a feature-rich high-level e621 and e926 API wrapper.

It provides access to almost all of the endpoints available. The only exceptions are unstable and admin-only endpoints.

e621 API documentation is currently highly undocumented, unstable, and sometimes even untruthful. We tried to wrap it in a sanest possible way, properly documenting all the possible ways to interact with it. However, if you still have any questions, bugs to report, or features to request -- please, create an issue on our [github page]("https://github.com/PatriotRossii/e621-py") and we will reply as soon as we can.


## Installation
```bash
$ pip install e621
```

## Quickstart
We translate everything the API returns to python data types created with pydantic. Everything is 100% typehinted so you get autocomplete everywhere and your IDE will warn you if you are sending invalid arguments or using nonexistent attributes.

### Creating the api client
* To create the most basic client, all you need to do is
```python
from e621 import E621

api = E621()
```

* If you wish to get information about your account, use your blacklist or create/update/delete any of the e621's entities, you will have to create an api key and put it into the API client as such:
```python
api = E621(("your_e621_login", "your_e621_api_key"))
```

### Searching
The majority of the endpoints allow you to query for a list of their entities, be it posts, pools or tags.
* To search for posts that match the "canine" but not the "3d" tag:
```python
posts = api.posts.search("canine -3d")
# Or
posts = api.posts.search(["canine", "-3d"])
```
* To search for pools whose names start with "hello" and end with "kitty":
```python
posts = api.pools.search(name_matches="hello*kitty")
```
* e621 searching api is paginated, which means that if you want to get a lot of posts, you will have to make multiple requests with a different "page" parameter. To simplify interactions with paginated queries, all of our searching endpoints support the "limit", "page", and "ignore_pagination" parameters. If you wish to get a specific number of entities, simply pass the "limit" and "ignore_pagination" arguments:
```python
tags = api.tags.search(name_matches="large_*", limit=900, ignore_pagination=True)
```
### Accessing Attributes
When you have retrieved the entities, you can access any of their attributes without dealing with json.
```python
for post in posts:
    print(post.score.total, post.all_tags, post.relationships.parent_id)
    with open(f"{post.id}.{post.file.ext}", "wb") as f:
        f.write(requests.get(post.file.url).content)
```
### Getting
Many entities that have unique identifiers (such as post_id or username) support indexing using these ids:
```python
post = api.posts.get(3291457)
posts = api.posts.get([3291457, 3069995])
pool = api.pools.get(28232)
user = api.users.get("fox")
```
### Updating
```python
api.posts.update(3291457, tag_string_diff="canine -male", description="Rick roll?")
```
### Creating
```python
from pathlib import Path

api.posts.create(
    tag_string="canine 3d rick_roll",
    file=Path("path/to/rickroll.webm"),
    rating="s",
    sources=[],
    description="Rick roll?"
)
```

## FAQ
* For more information on these and other api endpoints, please, visit our [endpoint reference](TODO)
