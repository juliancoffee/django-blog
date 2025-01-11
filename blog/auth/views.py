import logging

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class LoginView(DjangoLoginView):
    template_name = "blog/login.html"
    # if can't figure out the next page, redirect to home
    #
    # NOTE: can't use reverse() here, because it will lead to circular imports
    next_page = reverse_lazy("blog:index")


def instant_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponseRedirect(reverse("blog:index"))
