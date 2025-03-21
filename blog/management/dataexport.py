import logging
from datetime import datetime
from typing import Optional, TypedDict

from blog.models import Post

logger = logging.getLogger(__name__)

# TODO: should we use something better here? can we?
# It's all will get converted to JSON anyway, and it doesn't do dates.
DateTime = str


class UserData(TypedDict):
    # that's all for now
    username: str


class CommentData(TypedDict):
    comment_text: str
    pub_date: DateTime
    # NOTE: should be connected with username in UserData
    username: Optional[str]
    ip: Optional[str]


class PostData(TypedDict):
    post_text: str
    pub_date: DateTime
    comments: list[CommentData]


class Data(TypedDict):
    posts: list[PostData]
    users: list[UserData]


def format_date(d: datetime) -> str:
    return d.isoformat()


def get_post_data() -> list[PostData]:
    res = []
    # NOTE: ok, we're using prefetch_related here, because select_related only
    # works for foreign keys on object you're fetching.
    #
    # Comment isn't a foreign key on Post, it is the other way around.
    #
    # So from my understanding, prefetch_related does two things for us.
    #
    # - Fetch all Post's
    # - Fetch all Comment's where post_id in <all posts>
    # Get the result of two queries and cache it in QuerySet.
    #
    # The alternative would be to fetch comment_set for each post in a new
    # query, which is not ideal.
    #
    # NOTE: you need to call it with "comment_set", because that's what you'll
    # use in the end.
    # Not just "comment"
    for post in (
        Post.objects.all().order_by("pub_date").prefetch_related("comment_set")
    ):
        post_data: PostData = {
            "post_text": post.post_text,
            "pub_date": format_date(post.pub_date),
            "comments": [
                {
                    "comment_text": comment.comment_text,
                    "pub_date": format_date(comment.pub_date),
                    # TODO: add users
                    "username": None,
                    "ip": comment.commenter_ip,
                }
                for comment in post.comment_set.all()
            ],
        }
        res.append(post_data)

    return res


def get_user_data() -> list[UserData]:
    # TODO: implement
    return []


def get_all_data() -> Data:
    return {
        "posts": get_post_data(),
        "users": get_user_data(),
    }
