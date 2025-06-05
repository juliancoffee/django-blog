import logging
import pprint
from collections.abc import Sequence
from typing import Any, Final

from django.http import HttpRequest
from django.views.debug import SafeExceptionReporterFilter

logger = logging.getLogger(__name__)
pf = pprint.pformat

# max length in "characters", where character _probably_ means u32 codepoint
MAX_COMMENT_LENGTH: Final[int] = 1000
MAX_POST_LENGTH: Final[int] = 10_000


def safe_pf(d: dict[str, Any]) -> str:
    safe_filter = SafeExceptionReporterFilter()

    def cleaner(entry):
        key, val = entry
        if safe_filter.hidden_settings.findall(key):
            val = safe_filter.cleansed_substitute
        return key, val

    return pf(sorted(map(cleaner, d.items())))


def get_user_ip(request: HttpRequest):
    """Get user ip from `HTTP_X_FORWARDED_FOR` header

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

        logger.error(
            "No HTTP_X_FORWARDED_FOR header found: meta={meta}".format(
                meta=safe_pf(request.META)
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
