import os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render


@staff_member_required
def spylog(request) -> HttpResponse:
    # NOTE: idk where we should block requests here or in urlconfig?
    #
    # but it's not like this whole view follows any kind of best practices,
    # so should I care about it that much?
    #
    # I should probably use something like sentry for such purpose, but
    # well, it's a pet project
    #
    # and my pet is still a puppy
    #
    # meanwhile, it works okey-ish
    if os.environ.get("DEVMODE") is None:
        return HttpResponse(
            "sommry, debug view is not enabled, go back", status=403
        )

    with open(settings.DEBUG_LOGFILE) as f:
        return render(
            request,
            "blog/debug_view.html",
            # TODO: what if we could reverse it somehow?
            # that would suck with multiline logs though
            #
            # ok I just found out about datadog, it might be simpler to
            # integrate, at least they provide Docker image
            #
            # and hopefully some webview?
            {"debug_file": settings.DEBUG_LOGFILE, "content": f.read()},
        )
