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
    for post in Post.objects.all():
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

    return sorted(res, key=lambda p: datetime.fromisoformat(p["pub_date"]))


def get_user_data() -> list[UserData]:
    # TODO: implement
    return []


def get_all_data() -> Data:
    return {
        "posts": get_post_data(),
        "users": get_user_data(),
    }
