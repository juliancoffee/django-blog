from django.urls import path

from . import views

app_name = "notifications"
urlpatterns = [
    # auth
    path("settings/", views.settings, name="settings"),
]
