import logging

from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from .models import Post

logger = logging.getLogger()


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
    p = get_object_or_404(Post, pk=post_id)
    return render(
        request,
        "blog/detail.html",
        {
            "post": p,
            "comments": p.comment_set.all(),
        },
    )


def comment(request: HttpRequest, post_id) -> HttpResponse:
    def get_user_ip(request: HttpRequest):
        """Get user ip from HTTP_X_FORWARDER_FOR header

        If no such header found or unable to parse it, returns None.
        """
        # in theory, we could return REMOTE_ADDR on error, but it may as well
        # be localhost or something similarly useless, if you use any proxies
        #
        # so if in doubt, just assume unknown
        ip_chain = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip_chain is None:
            logger.error(
                f"No HTTP_X_FORWARDER_FOR header found: meta={request.META}"
            )
            return None

        match ip_chain.split(","):
            case [main_ip, *_]:
                return main_ip
            case rest:
                logger.error(f"Unexpected HTTP_X_FORWARDER_FOR split: {rest}")
                return None

    p = get_object_or_404(Post, pk=post_id)
    # p. s. this could be pattern match (or if) on .get()
    try:
        comment = request.POST["comment"]
    except KeyError:
        logger.error(f"Couldn't find comment in the form: POST={request.POST}")
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
