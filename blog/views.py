import logging
import os
import pprint
from collections.abc import Sequence

from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.debug import SafeExceptionReporterFilter

from .models import Post

logger = logging.getLogger()

pf = pprint.pformat


# Create your views here.
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
        },
    )


def comment(request: HttpRequest, post_id) -> HttpResponse:
    def get_user_ip(request: HttpRequest):
        """Get user ip from HTTP_X_FORWARDED_FOR header

        If no such header found or unable to parse it, returns None.
        """
        # in theory, we could return REMOTE_ADDR on error, but it may as well
        # be localhost or something similarly useless, if you use any proxies
        #
        # so if in doubt, just assume unknown
        ip_chain = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip_chain is None:
            # NOTE: request.META includes a lot of stuff in plaintext, including
            # SECRET_KEY, so be careful with showing it
            safe_filter = SafeExceptionReporterFilter()

            def cleaner(entry):
                key, val = entry
                if safe_filter.hidden_settings.findall(key):
                    val = safe_filter.cleansed_substitute
                return key, val

            logger.error(
                "No HTTP_X_FORWARDED_FOR header found: meta={meta}".format(
                    meta=pf(sorted(map(cleaner, request.META.items())))
                )
            )
            return None

        chain: Sequence[str] = ip_chain.split(",")
        match chain:
            case [main_ip, *_] if main_ip:
                return main_ip
            case _split:
                err_msg = (
                    f"Unexpected HTTP_X_FORWARDED_FOR={ip_chain!r}: {_split=}"
                )
                logger.error(err_msg)
                return None

    p = get_object_or_404(Post, pk=post_id)
    # p. s. this could be pattern match (or if) on .get()
    try:
        comment = request.POST["comment"]
    except KeyError:
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
            },
        )
    else:
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
            {"debug_file": settings.DEBUG_LOGFILE, "content": f.read()},
        )
