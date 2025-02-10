from datetime import datetime
from typing import Optional, TypedDict

from django.http import FileResponse

from blog.models import Post

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


class ExportData(TypedDict):
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
            # TODO: add comments
            "comments": [],
        }
        res.append(post_data)

    return res


def get_user_data() -> list[UserData]:
    # TODO: implement
    return []


def get_all_data() -> ExportData:
    return {
        "posts": get_post_data(),
        "users": get_user_data(),
    }


# Create your views here.
def export(request) -> FileResponse:
    raise NotImplementedError
