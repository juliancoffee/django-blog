import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.base import View

logger = logging.getLogger(__name__)


class LoginView(DjangoLoginView):
    template_name = "blog/login.html"
    # if can't figure out the next page, redirect to home
    #
    # NOTE: can't use reverse() here, because it will lead to circular imports
    next_page = reverse_lazy("blog:index")


# NOTE: that must be POST method, not GET
#
# While it's easy to make it a GET request and fire via the link, GET shouldn't
# be used for that.
#
# GET is considered a "safe" method and omits a lot of security checks, but
# logout is a bit of a destructive operation, so yeah...
#
# And because we can't use GET and I don't want to have a separate logout page,
# because that'd be super annoying I have two options
# 1) wrap it in the invisible form
# 2) make a button and place a JS fetch on it
#
# And I went with the third option, HTMX, because why not?
#
# So, HTMX has its own set of quirks.
# 1) One of the points of HTMX are partial updates via template fragments.
# I.e. instead of sending whole HTML document, we only send required part.
#
# Which is cool, but would require to potentially refactor my whole template
# folder, and I don't want to do that, so I just won't do that.
#
# 2) If we're not going to send partial updates, we would keep plain redirects
# but for some reason HTMX doesn't recognise them.
#
# It does have the ability to do that via the custom header, so that's what
# we're using.
#
# P. S. I might re-design my templates later into using fragments.
# Django should allow that with their {% include "other.html" %} directive.
@require_POST
def instant_logout(request: HttpRequest) -> HttpResponse:
    logout(request)

    response = HttpResponse()
    response.headers["HX-Redirect"] = reverse("blog:index")
    return response

# NOTE:
# We use method decorator on "dispatch" because that's an entry point.
#
# sort of
#
# I just realized that I'm not sure how exactly LoginRequired middleware checks
# which requests to allow and which to discard.
#
# Although if I remember it correctly from looking at Django's source code and
# `as_view()` method in general, it copies attributes from dispatch method to
# the returned view function.
#
# So I guess that is the reason why we put the decorator on dispatch.
#
# But I don't think I'll *understand* the behaviour until I'll write my own
# middleware.
@method_decorator(login_not_required, name="dispatch")
class SignUpView(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return render(request, "blog/signup.html")
