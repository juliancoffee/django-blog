import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, assert_never

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.http import HttpRequest

from blog.models import Post

from .dataexport import CommentData as ExportCommentData
from .dataexport import Data as ExportData
from .dataexport import PostData as ExportPostData
from .forms import ImportDataForm
from .utils import Err, Ok, Result

logger = logging.getLogger(__name__)


@dataclass
class CommentData:
    comment_text: str
    pub_date: datetime
    ip: Optional[str]


@dataclass
class PostData:
    post_text: str
    pub_date: datetime
    comments: list[CommentData]


@dataclass
# TODO: add users
class Data:
    posts: list[PostData]


def convert_post(json_post: ExportPostData) -> PostData:
    text = json_post["post_text"]
    date = datetime.fromisoformat(json_post["pub_date"])

    comments = list(map(convert_comment, json_post["comments"]))
    return PostData(post_text=text, pub_date=date, comments=comments)


def convert_comment(json_comment: ExportCommentData) -> CommentData:
    text = json_comment["comment_text"]
    date = datetime.fromisoformat(json_comment["pub_date"])
    ip = json_comment["ip"]
    return CommentData(comment_text=text, pub_date=date, ip=ip)


def parse_import_data(
    request: HttpRequest,
) -> Result[Data, ImportDataForm]:
    """Returns the data along with the form or gives just form with errors"""
    form = ImportDataForm(request.POST, request.FILES)
    if not form.is_valid():
        return Result.err(form)

    data_file = request.FILES["data_file"]
    # Ok, I hope that I won't ever pass multiple files here.
    # If I do, let it crash
    #
    # And no, I won't run my code with `python -O`.
    # I hope...
    assert isinstance(data_file, UploadedFile)

    raw_data = data_file.read()
    json_data: ExportData = json.loads(raw_data)
    posts = list(map(convert_post, json_data["posts"]))

    parsed_data = Data(posts=posts)
    return Result.ok(parsed_data)


@transaction.atomic
def load_all_data_in(
    request: HttpRequest,
) -> Result[tuple[int, int], ImportDataForm]:
    # Logic considerations:
    #
    # 1) We probably don't want to duplicate existing posts.
    # Yeah, hopefully string-equality algorithms are fast enough.
    # 2) What should we do if existing post has different set of comments?
    # For now, we'll just ignore the post if it exists.
    # 3) Should we create users if they don't exist?
    # For now, we don't have users.
    # 4) Should we assign comments to existing users, if found?
    # For now, we don't have user info to comments.

    # Perfomance considerations:
    # - First of all, that's the coldest code possible, it's supposed to run once
    # per ... month, at best.
    # - Additionally, I think the slowest part would be data-fetching, so we're
    # doing that only once.
    #
    # Well, except then we're doing data-insert, which would be much slower, but
    # maybe Django's ORM can optimise it somehow?

    # Integrity considertations:
    # - The function is wrapped with @transaction.atomic, it will do automatic
    # rollback if any exception is encountered

    match parse_import_data(request).get():
        case Err(form):
            return Result.err(form)
        case Ok(d):
            data = d
        case r:
            assert_never(r)

    # Algorithmic shenanigans
    # Build skiplist for duplicates via two O(n) passes instead of a nested loop
    post_map: dict[str, PostData] = {p.post_text: p for p in data.posts}
    duplicates: set[str] = set(
        p.post_text for p in Post.objects.all() if p.post_text in post_map
    )

    post_counter = 0
    comment_counter = 0
    for text, post in post_map.items():
        if text in duplicates:
            continue

        p = Post(post_text=post.post_text, pub_date=post.pub_date)
        p.save()
        post_counter += 1

        for c in post.comments:
            p.comment_set.create(
                comment_text=c.comment_text,
                pub_date=c.pub_date,
                commenter_ip=c.ip,
            )
            comment_counter += 1

    return Result.ok((post_counter, comment_counter))
