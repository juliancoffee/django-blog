import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import SubscribeForm
from .models import Subscription

logger = logging.getLogger(__name__)


# Create your views here.
def handle_settings_update(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


def settings_page(request: HttpRequest) -> HttpResponse:
    # this page requires auth, plus we're using LoginRequiredMiddleware
    assert request.user.is_authenticated

    user_subs = Subscription.objects.filter(user=request.user).first()
    if user_subs is not None:
        # p. s. it kind of sucks that I must provide a dictionary here and lose
        # type-checking
        form_data = {
            "to_new_posts": user_subs.to_new_posts,
            "to_engaged_posts": user_subs.to_engaged_posts,
        }
    else:
        form_data = {}

    # pre-populate the form
    form = SubscribeForm(form_data)

    return render(
        request,
        "blog/notif_settings.html",
        {
            "form": form,
        },
    )


# Should I cave in and just write everything in class-based views?
def settings(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return settings_page(request)
    elif request.method == "POST":
        return handle_settings_update(request)
    else:
        raise NotImplementedError
