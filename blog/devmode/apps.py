from django.apps import AppConfig


class DevModeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog.devmode"
