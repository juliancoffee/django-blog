import io
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypedDict

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import UploadedFile
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from blog.models import Post

from .forms import ImportDataForm

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


# We know that all users are authorized, because of LoginRequiredMiddleware
#
# I'm not sure I like the fact that it is so implicit and can't be inferred
# from the function body, but whatever.
#
# Also I don't like that fact that our authentication check is automatic,
# but our authorization check can be ignored.
#
# Of course, you can't automate authorization, but can't we at least have
# some catch-all check that forbids every request, unless configured?
def user_is_staff_check(user: User | AnonymousUser) -> bool:
    return user.is_staff


# Create your views here.
@user_passes_test(user_is_staff_check)
def export_page(request: HttpRequest) -> HttpResponse:
    form = ImportDataForm()
    return render(
        request,
        "blog/export_page.html",
        {
            "form": form,
        },
    )


@user_passes_test(user_is_staff_check)
def export_data(request: HttpRequest) -> HttpResponse:
    response = HttpResponse()
    response.headers["HX-Redirect"] = reverse("blog:export_file")
    return response


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

    return FileResponse(databuff, as_attachment=True, filename="data.json")


@dataclass
class ImportPostData:
    post_text: str
    pub_date: datetime


@dataclass
# TODO: add users
class ImportData:
    posts: list[ImportPostData]


# Shouldn't we return something here? Status code or smth.
# Just raise an exception?
#
# Gosh, how do people live without enums.
def parse_import_data(request: HttpRequest) -> Optional[ImportData]:
    form = ImportDataForm(request.POST, request.FILES)
    if not form.is_valid():
        raise RuntimeError("form is invalid, {form.errors.get_json_data()}")

    data_file = request.FILES["data_file"]
    # WHY DJANGO, WHY?
    assert isinstance(data_file, UploadedFile)

    if data_file.content_type != "application/json":
        raise RuntimeError(
            f"expected application/json, got {data_file.content_type}"
        )
    raw_data = data_file.read()
    json_data: ExportData = json.loads(raw_data)

    posts: list[ImportPostData] = []
    for post in json_data["posts"]:
        text = post["post_text"]
        date = datetime.fromisoformat(post["pub_date"])
        posts.append(ImportPostData(text, date))
    parsed_data = ImportData(posts=posts)
    return parsed_data


def load_all_data_in() -> None:
    raise NotImplementedError


@user_passes_test(user_is_staff_check)
def import_preview(request: HttpRequest) -> HttpResponse:
    data = parse_import_data(request)
    return render(request, "blog/import_preview_fragment.html", {"data": data})


@user_passes_test(user_is_staff_check)
def import_data(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<p> sommry, not implemented yet </p>")
