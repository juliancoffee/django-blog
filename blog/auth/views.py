import logging

from django.contrib.auth.views import LoginView as DjangoLoginView

logger = logging.getLogger(__name__)


class LoginView(DjangoLoginView):
    template_name = "blog/login.html"
    # if can't figure out the next page, redirect to home
    next_page="/index"
