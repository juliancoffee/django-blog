import logging

from django.contrib.auth.decorators import login_not_required
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

logger = logging.getLogger(__name__)


@login_not_required
def login(request: HttpRequest) -> HttpResponse:
    next_page = request.GET.get("next")
    logging.debug(f"{next_page=}")
    return render(
        request,
        "blog/login.html",
        {
            "next": next_page,
        },
    )
