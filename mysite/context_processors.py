from django.conf import settings


def dev_mode(request):
    return {
        "dev_mode": settings.DEV_MODE,
    }
