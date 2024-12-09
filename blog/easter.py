import os
import random
from unittest import TestResult

from django.test import TestCase


# please, pretend that you didn't see it
class PredictionGenerator(TestCase):
    __doc__ = random.choice(
        [
            "Linux will be rewritten in Python by 2050. Get ready!",
            "RustPython will be the official interpreter by 2035!",
            "I can't believe this is possible.",
            "9.11 > 9.9, we consulted AI.",
            "Do you believe in Guido?",
            "Dit is duidelijk!",
        ]
    )

    def __call__(self, result: TestResult | None = None) -> None:
        if os.environ.get("PY_PREDICT") is None:
            return
        self.assertIs(True, False)
