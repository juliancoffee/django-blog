import io
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypedDict

from django.contrib.auth.decorators import user_passes_test
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render

from blog.models import Post
from blog.utils import user_is_staff_check

from .forms import ExportDataForm, ImportDataForm

logger = logging.getLogger(__name__)

# TODO: should we use something better here? can we?
# It's all will get converted to JSON anyway, and it doesn't do dates.
DateTime = str


class ExportUserData(TypedDict):
    # that's all for now
    username: str


class ExportCommentData(TypedDict):
    comment_text: str
    pub_date: DateTime
    # NOTE: should be connected with username in UserData
    username: Optional[str]
    ip: Optional[str]


class ExportPostData(TypedDict):
    post_text: str
    pub_date: DateTime
    comments: list[ExportCommentData]


class ExportData(TypedDict):
    posts: list[ExportPostData]
    users: list[ExportUserData]


def format_date(d: datetime) -> str:
    return d.isoformat()


def get_post_data() -> list[ExportPostData]:
    res = []
    for post in Post.objects.all():
        post_data: ExportPostData = {
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


def get_user_data() -> list[ExportUserData]:
    # TODO: implement
    return []


def get_all_data() -> ExportData:
    return {
        "posts": get_post_data(),
        "users": get_user_data(),
    }


# Create your views here.
@user_passes_test(user_is_staff_check)
def data_console(request: HttpRequest) -> HttpResponse:
    import_form = ImportDataForm()
    export_form = ExportDataForm()
    return render(
        request,
        "blog/export_page.html",
        {
            "import_form": import_form,
            "export_form": export_form,
        },
    )


# NOTE: It's a GET request, but we're safe.
#
# The only case where this might be a problem is if another browser makes
# a fetch request behind the scenes, but CORS policies wouldn't allow that.
#
# - If you just visit this page via browser, that's completely fine, we will
# check authentication and authorization server-side.
# - If you visit this page with something like a `curl`, you simply won't pass
# auth.
@user_passes_test(user_is_staff_check)
def export_datafile(request: HttpRequest) -> HttpResponse | FileResponse:
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

    return FileResponse(
        databuff,
        as_attachment="download" in request.GET,
        filename="data.json",
    )


@dataclass
class ImportCommentData:
    comment_text: str
    pub_date: datetime
    ip: Optional[str]


@dataclass
class ImportPostData:
    post_text: str
    pub_date: datetime
    comments: list[ImportCommentData]


@dataclass
# TODO: add users
class ImportData:
    posts: list[ImportPostData]


def convert_post(json_post: ExportPostData) -> ImportPostData:
    text = json_post["post_text"]
    date = datetime.fromisoformat(json_post["pub_date"])

    comments = list(map(convert_comment, json_post["comments"]))
    return ImportPostData(post_text=text, pub_date=date, comments=comments)


def convert_comment(json_comment: ExportCommentData) -> ImportCommentData:
    text = json_comment["comment_text"]
    date = datetime.fromisoformat(json_comment["pub_date"])
    ip = json_comment["ip"]
    return ImportCommentData(comment_text=text, pub_date=date, ip=ip)


# Shouldn't we return something here? Status code or smth.
# Just raise an exception?
#
# Gosh, how do people live without enums.
def parse_import_data(request: HttpRequest) -> ImportData:
    form = ImportDataForm(request.POST, request.FILES)
    if not form.is_valid():
        # TODO: make HTMX work with this
        raise RuntimeError("form is invalid, {form.errors.get_json_data()}")

    data_file = request.FILES["data_file"]
    # WHY DJANGO, WHY?
    assert isinstance(data_file, UploadedFile)

    if data_file.content_type != "application/json":
        # TODO: make HTMX work with this
        raise RuntimeError(
            f"expected application/json, got {data_file.content_type}"
        )

    raw_data = data_file.read()
    json_data: ExportData = json.loads(raw_data)
    posts = list(map(convert_post, json_data["posts"]))

    parsed_data = ImportData(posts=posts)
    return parsed_data


@user_passes_test(user_is_staff_check)
def import_preview(request: HttpRequest) -> HttpResponse:
    data = parse_import_data(request)
    return render(request, "blog/import_preview_fragment.html", {"data": data})


@transaction.atomic
def load_all_data_in(request: HttpRequest) -> Optional[tuple[int, int]]:
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

    data = parse_import_data(request)
    # Algorithmic shenanigans
    # Build skiplist for duplicates via two O(n) passes instead of a nested loop
    post_map: dict[str, ImportPostData] = {p.post_text: p for p in data.posts}
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

    return post_counter, comment_counter


@user_passes_test(user_is_staff_check)
def import_data(request: HttpRequest) -> HttpResponse:
    counters = None
    try:
        counters = load_all_data_in(request)
    except Exception:
        logger.error("failed to import the data", exc_info=True)

    if counters is not None:
        posts, comments = counters
        return HttpResponse(
            "<p>import completed! {} posts, {} comments </p>".format(
                posts, comments
            )
        )
    else:
        return HttpResponse("<p>sommry, something went wrong</p>")
