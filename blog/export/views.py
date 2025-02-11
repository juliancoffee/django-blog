import io
import json
import logging
from datetime import datetime
from typing import Optional, TypedDict

from django.http import FileResponse, HttpRequest, HttpResponse

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
def export(request: HttpRequest) -> HttpResponse | FileResponse:
    # NOTE: we know that all users are authorized, because of login required
    # middleware.
    #
    # I'm not sure I like the fact that it is so implicit and can't be inferred
    # from the function body, but whatever.
    if not request.user.is_staff:
        return HttpResponse("nope, you can't do that", status=403)

    # TODO: this should probably have some filtering and stuff, because we're
    # practically loading our whole database into memory at once, but whatever.
    #
    # For now, my blog doesn't have any users except me, really, so it's ok.
    databuff = io.BytesIO()
    data = get_all_data()

    # I couldn't get json output the data into the buffer, mypy was mad at me.
    #
    # It is happy with this code although it's probably less efficient.
    databuff.write(json.dumps(data).encode())
    # NOTE: don't forget to seek to the beginning
    databuff.seek(0)

    return FileResponse(databuff, as_attachment=True, filename="data.json")
