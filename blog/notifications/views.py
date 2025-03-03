import logging

from django.contrib.auth.models import User
from django.db.models import BooleanField, Case, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import SubscribeForm

logger = logging.getLogger(__name__)


# Create your views here.
def handle_settings_update(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


def settings_page(request: HttpRequest) -> HttpResponse:
    user_subs = (
        User.objects.filter(id=request.user.id)
        .annotate(
            to_new_posts=Case(
                When(newpostsubscriber__isnull=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            to_engaged_posts=Case(
                When(engagedpostsubscriber__isnull=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
        .first()
    )
    assert user_subs is not None

    # pre-populate the form
    #
    # p. s. it kind of sucks that I must provide a dictionary here and lose
    # type-checking
    form = SubscribeForm(
        {
            "to_new_posts": user_subs.to_new_posts,
            "to_engaged_posts": user_subs.to_engaged_posts,
        }
    )

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
