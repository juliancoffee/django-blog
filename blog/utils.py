import logging
import pprint
from collections.abc import Callable, Sequence
from typing import TypeVar

from django.contrib.auth.models import AnonymousUser, User
from django.http import (
    HttpRequest,
)
from django.views.debug import SafeExceptionReporterFilter

logger = logging.getLogger(__name__)
pf = pprint.pformat


F = TypeVar("F")
TestProvider = Callable[[], list[tuple]]


def test_with(test_provider: TestProvider) -> Callable[[F], F]:
    def decorator(view_func):
        view_func.test_provider = test_provider  # type: ignore
        return view_func

    return decorator


# We know that all users are authorized, because of LoginRequiredMiddleware
#
# I'm not sure I like the fact that it is so implicit and can't be inferred
# from the function body, but whatever.
#
# Also I don't like that fact that our authentication check is automatic,
# but our authorization check can be ignored.
#
# Of course, you can't automate authorization, but can't we at least have
# some catch-all check that forbids every request, unless configured?
def user_is_staff_check(user: User | AnonymousUser) -> bool:
    return user.is_staff


def get_user_ip(request: HttpRequest):
    """Get user ip from HTTP_X_FORWARDED_FOR header

    If no such header found or unable to parse it, returns None.
    """
    # in theory, we could return REMOTE_ADDR on error, but it may as well
    # be localhost or something similarly useless, if you use any proxies
    #
    # so if in doubt, just assume unknown
    ip_chain = request.META.get("HTTP_X_FORWARDED_FOR")
    if ip_chain is None:
        # NOTE: request.META includes a lot of stuff in plaintext, including
        # SECRET_KEY, so be careful with showing it
        safe_filter = SafeExceptionReporterFilter()

        def cleaner(entry):
            key, val = entry
            if safe_filter.hidden_settings.findall(key):
                val = safe_filter.cleansed_substitute
            return key, val

        logger.error(
            "No HTTP_X_FORWARDED_FOR header found: meta={meta}".format(
                meta=pf(sorted(map(cleaner, request.META.items())))
            )
        )
        return None

    chain: Sequence[str] = ip_chain.split(",")
    match chain:
        case [main_ip, *_] if main_ip:
            return main_ip
        case _split:
            err_msg = f"Unexpected HTTP_X_FORWARDED_FOR={ip_chain!r}: {_split=}"
            logger.error(err_msg)
            return None
