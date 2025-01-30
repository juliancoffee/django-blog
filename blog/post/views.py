import logging
import pprint

from django.contrib.auth.decorators import login_not_required
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from blog.utils import get_user_ip

from .forms import CommentForm
from .models import Post

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


# TODO: remove this, it's temporary
# @login_not_required
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
            "form": CommentForm(),
        },
    )


@method_decorator(login_not_required, name="dispatch")
class CommentView(FormView):
    template_name = "blog/detail.html"
    form_class = CommentForm
    http_method_names = ["post"]

    def form_invalid(self, form):
        form_data = self.request.POST.dict()
        logger.error(f"Couldn't find comment in the form: POST={pf(form_data)}")

        return super().form_invalid(form)

    def form_valid(self, form):
        post_id: int = self.kwargs["post_id"]
        p = get_object_or_404(Post, pk=post_id)

        comment = form.cleaned_data["comment"]
        comment_data = {}
        if (ip := get_user_ip(self.request)) is not None:
            comment_data["commenter_ip"] = ip
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            user = None

        logger.debug(f"{comment_data=}")

        p.comment_set.create(
            comment_text=comment,
            pub_date=timezone.now(),
            commenter=user,
            **comment_data,
        )
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        #
        # ^ source: Django Docs, Tutorial part 4
        return HttpResponseRedirect(reverse("blog:detail", args=(post_id,)))
