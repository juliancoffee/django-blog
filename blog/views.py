import logging
import pprint

from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from mysite.utils.testing import test_with

from .forms import CommentForm
from .models import Post
from .utils import get_user_ip
from .utils.testing import random_post_ids

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
@test_with(random_post_ids)
def detail(request, post_id: int) -> HttpResponse:
    # NOTE: We do two SQL queries, one to get the post, another to get the
    # comments.
    # We could in theory, first get all the comments for this post, and then
    # select_related("post") and do a JOIN, which would result in us doing just
    # one query.
    # Would it be faster? Probably ...?
    # It would consume much more memory though, because we'd duplicate the post
    # each time, and posts contain text, which makes them kinda heavy.
    # 200 characters = 200 bytes.
    # Now multiply it by number of comments.
    #
    # Probably doesn't matter either way at this scale, so we're just letting
    # Django do it's thing and issue two queries.
    #
    # P. S. I think I saw more than two queries with Django Debug Toolbar.
    # I don't want to look into it right now though.
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
@method_decorator(test_with(random_post_ids), name="dispatch")
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
        user = self.request.user if self.request.user.is_authenticated else None

        p.comment_set.create(
            comment_text=comment,
            pub_date=timezone.now(),
            commenter=user,
            commenter_ip=get_user_ip(self.request),
        )
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        #
        # ^ source: Django Docs, Tutorial part 4
        return HttpResponseRedirect(reverse("blog:detail", args=(post_id,)))
