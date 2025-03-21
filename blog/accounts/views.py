import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView

from .forms import UpdateEmailForm

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
# << source code explanation >>
# Judging by the code, as_view() copies attributes from `dispatch` method
# to the resulting callable.
# On of such attributes is "login_required" which can be True or False, which
# is then checked by LoginRequiredMiddleware, if such exists, of course.
# login_not_required() decorator sets this attribute to False, but by default
# LoginRequireMiddleware
# << end of source code explanation >>
#
# That's a neat hack, I must say.
@method_decorator(login_not_required, name="dispatch")
class SignUpView(FormView):
    template_name = "blog/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("blog:index")

    def form_valid(self, form):
        # else, register the user
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]

        user = User.objects.create_user(username, None, password)
        user.save()

        # this should always pass, after all, we have just created this user
        logged_user = authenticate(username=username, password=password)
        assert logged_user is not None

        # for convenience sake, log in the user right there
        login(self.request, logged_user)

        return super().form_valid(form)


def profile(request: HttpRequest) -> HttpResponse:
    email_form = UpdateEmailForm()
    return render(request, "blog/profile.html", {"email_form": email_form})


@require_POST
def update_email(request: HttpRequest) -> HttpResponse:
    # assert mainly to convince `mypy`, but also as a safety net
    # we're using LoginNotRequiredMiddleware anyway
    assert request.user.is_authenticated

    form = UpdateEmailForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "blog/email_form_fragment.html",
            {
                "form": form,
            },
        )
    user = request.user
    # NOTE: ideally we'd send confirmation email here, but it's ... fine for now
    # It's not an outright security vulnerability, probably.
    user.email = form.cleaned_data["email"]
    user.save()

    response = HttpResponse()
    response.headers["HX-Redirect"] = reverse("blog:accounts:profile")
    return response
