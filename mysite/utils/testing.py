import logging
import pprint
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)
pf = pprint.pformat


F = TypeVar("F")
TestProvider = Callable[[], list[tuple]]


def test_with(test_provider: TestProvider) -> Callable[[F], F]:
    def decorator(view_func):
        view_func.test_provider = test_provider  # type: ignore
        return view_func

    return decorator
