import logging
import os
import pprint

from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .models import Post
from .utils import get_user_ip

logger = logging.getLogger()

pf = pprint.pformat


# Create your views here.
@login_not_required
def index(request) -> HttpResponse:
    # only show posts that already have been published
    # i. e. ones with pub_date less than or equal to 'now'
    #
    # p. s. that's the weirdest ORM syntax I've ever seen (not that I've seen
    # many)
    # p. p. s and of course, mypy can't catch any mistakes here, that sucks
    posts = Post.objects.filter(pub_date__lte=timezone.now()).order_by(
        "-pub_date"
    )
    context = {"post_list": posts}
    return render(request, "blog/index.html", context)


@login_not_required
def detail(request, post_id: int) -> HttpResponse:
    # TODO: this is premature optimization
    #
    # but
    #
    # we do two SQL queries here
    #
    # one to get the post with such id
    # second to get all the comments for such id
    #
    # couldn't this be just one query with a join or smth?
    #
    # I mean, we would still need data for post itself
    #
    # its pub_data and post_text, but it's hard to imagine something
    # be as slow in this world as an another SQL query
    #
    # I guess I could run it live with DJDT enabled and check the timings
    #
    # and then I could try to optimize it just for fun
    #
    # I couldn't find exactly JOIN, but I found something like prefetch_related
    # and select_related
    p = get_object_or_404(Post, pk=post_id)
    return render(
        request,
        "blog/detail.html",
        {
            "post": p,
            "comments": p.comment_set.all(),
            "error": [],
            "form": CommentForm(),
        },
    )


# TODO: handle anonymours and logged-on users properly
@login_not_required
# p. s. require_POST sure has a fun behaviour where it spits out empty page
# on wrong HTTP method
@require_POST
def comment(request: HttpRequest, post_id) -> HttpResponse:
    p = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.cleaned_data["comment"]
        match get_user_ip(request):
            case None:
                p.comment_set.create(
                    comment_text=comment, pub_date=timezone.now()
                )
            case ip:
                p.comment_set.create(
                    comment_text=comment,
                    pub_date=timezone.now(),
                    commenter_ip=ip,
                )
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        #
        # ^ source: Django Docs, Tutorial part 4
        return HttpResponseRedirect(reverse("blog:detail", args=(post_id,)))
    else:
        logger.error(
            f"Couldn't find comment in the form: POST={pf(request.POST.dict())}"
        )

        return render(
            request,
            "blog/detail.html",
            {
                "post": p,
                "comments": p.comment_set.all(),
                "error": "we couldn't get your comment, sommry!",
                "form": CommentForm(),
            },
        )


def debug_view(request) -> HttpResponse:
    # NOTE: idk where we should block requests here or in urlconfig?
    #
    # but it's not like this whole view follows any kind of best practices,
    # so should I care about it that much?
    #
    # I should probably use something like sentry for such purpose, but
    # well, it's a pet project
    #
    # and my pet is still a puppy
    #
    # meanwhile, it works okey-ish
    if os.environ.get("DEVMODE") is None:
        return HttpResponse(
            "sommry, debug view is not enabled, go back", status=403
        )

    with open(settings.DEBUG_LOGFILE) as f:
        return render(
            request,
            "blog/debug_view.html",
            # TODO: what if we could reverse it somehow?
            # that would suck with multiline logs though
            #
            # ok I just found out about datadog, it might be simpler to
            # integrate, at least they provide Docker image
            #
            # and hopefully some webview?
            {"debug_file": settings.DEBUG_LOGFILE, "content": f.read()},
        )
