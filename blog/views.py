import logging
import pprint
from collections.abc import Sequence
from typing import Any, TypedDict, override

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from mysite.utils.testing import test_with

from .forms import CommentForm, PostForm
from .models import Comment, Post
from .utils import get_user_ip, safe_pf
from .utils.testing import random_post_ids

logger = logging.getLogger()

pf = pprint.pformat


class PostDetail(TypedDict):
    id: int
    post_text: str


def post_data() -> Sequence[PostDetail]:
    return [
        {
            "id": post_id,
            "post_text": post_text,
        }
        for post_id, post_text in Post.objects.filter(
            # only show posts that already have been published
            # i. e. ones with pub_date less than or equal to 'now'
            pub_date__lte=timezone.now()
        )
        .order_by("-pub_date")
        .values_list("id", "post_text")
    ]


# Create your views here.
@login_not_required
def index(request) -> HttpResponse:
    context = {
        "posts": post_data(),
        "form": PostForm() if request.user.is_staff else None,
    }
    return render(request, "blog/index.html", context)


@method_decorator(staff_member_required, name="dispatch")
class PostView(FormView):
    """
    Handles dynamic post submissions
    """

    template_name = "blog/post_list_fragment.html"
    form_class = PostForm
    http_method_names = ["post"]

    @override
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Insert the form and template arguments into context
        """
        context = super().get_context_data(**kwargs)

        context["posts"] = post_data()
        return context

    @override
    def form_invalid(self, form):
        """
        Return back the post list and the form with errors
        """
        form_data = self.request.POST.dict()
        logger.error(
            f"Couldn't find post in the form: POST={safe_pf(form_data)}"
        )

        context = self.get_context_data(**self.kwargs)
        return self.render_to_response(context=context)

    @override
    def form_valid(self, form) -> HttpResponse:
        """
        Create a new post and render the new post list
        """
        text = form.cleaned_data["post"]
        date = timezone.now()

        # create the post
        post = Post(post_text=text, pub_date=date)
        post.save()

        # re-fetch comments and render the _new_ form
        context = self.get_context_data(**self.kwargs)
        context["form"] = self.form_class()
        return self.render_to_response(context=context)


class CommentDetail(TypedDict):
    author_username: str
    comment_text: str


def comment_data(post_id: int) -> Sequence[CommentDetail]:
    # eagerly evaluate to control when it runs
    return [
        {
            "author_username": username,
            "comment_text": comment_text,
        }
        for (
            username,
            comment_text,
        ) in Comment.objects.filter(post_id=post_id)
        .order_by("pub_date")
        .values_list("commenter__username", "comment_text")
    ]


@login_not_required
@test_with(random_post_ids)
def detail(request, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    return render(
        request,
        "blog/detail.html",
        {
            "post": post,
            "comments": comment_data(post_id),
            "form": CommentForm(),
        },
    )


@method_decorator(login_not_required, name="dispatch")
@method_decorator(test_with(random_post_ids), name="dispatch")
class CommentView(FormView):
    """
    Handles dynamic comment submissions
    """

    template_name = "blog/comment_list_fragment.html"
    form_class = CommentForm
    http_method_names = ["post"]

    @override
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Insert the form and template arguments into context
        """
        context = super().get_context_data(**kwargs)
        # NOTE: only self.kwargs guarantees to store query params
        post_id = self.kwargs["post_id"]

        context["post"] = {"id": post_id}
        context["comments"] = comment_data(post_id)
        return context

    @override
    def form_invalid(self, form):
        """
        Return back the comment list and the form with errors
        """
        form_data = self.request.POST.dict()
        logger.error(
            f"Couldn't find comment in the form: POST={safe_pf(form_data)}"
        )

        context = self.get_context_data(**self.kwargs)
        return self.render_to_response(context=context)

    @override
    def form_valid(self, form):
        """
        Create a new comment and render the new comment list
        """
        post_id = self.kwargs["post_id"]

        user = self.request.user if self.request.user.is_authenticated else None

        # INFO:
        # Using this and not `Post.get(pk=post).comment_set` to avoid separate
        # query
        comment = Comment(
            post_id=post_id,
            comment_text=form.cleaned_data["comment"],
            pub_date=timezone.now(),
            commenter=user,
            commenter_ip=get_user_ip(self.request),
        )
        comment.save()

        # re-fetch comments and render the _new_ form
        context = self.get_context_data(**self.kwargs)
        context["form"] = self.form_class()
        return self.render_to_response(context=context)
