import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import SubscribeForm
from .models import Subscription

logger = logging.getLogger(__name__)


# Create your views here.
def handle_settings_update(request: HttpRequest) -> HttpResponse:
    # this page requires auth, plus we're using LoginRequiredMiddleware
    # NOTE: `assert` here is mainly for `mypy`
    assert request.user.is_authenticated

    form = SubscribeForm(request.POST)

    if not form.is_valid():
        return render(
            request,
            "blog/notif_settings.html",
            {
                "form": form,
            },
        )

    user_subs = Subscription.objects.get_or_create(user=request.user)[0]
    user_subs.to_new_posts = form.cleaned_data["to_new_posts"]
    user_subs.to_engaged_posts = form.cleaned_data["to_engaged_posts"]
    # imagine if there was a context-manager that automatically calls save() ...
    #
    # dreams, sweat dreams
    user_subs.save()

    return HttpResponseRedirect(reverse("blog:notifications:settings"))


def settings_page(request: HttpRequest) -> HttpResponse:
    # this page requires auth, plus we're using LoginRequiredMiddleware
    # NOTE: `assert` here is mainly for `mypy`
    assert request.user.is_authenticated

    # pre-populate the form
    user_subs = Subscription.objects.get_or_create(user=request.user)[0]
    form = SubscribeForm(instance=user_subs)

    return render(
        request,
        "blog/notif_settings.html",
        {
            "form": form,
        },
    )


# Should I cave in and just write everything in class-based views?
@require_http_methods(["GET", "POST"])
def settings(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return settings_page(request)
    elif request.method == "POST":
        return handle_settings_update(request)
    else:
        # yes, this is unreachable for now, but I'd like to get an error here
        # if this code changes in some unpredicable way
        raise RuntimeError(f"unreachable, {request.method=}")
