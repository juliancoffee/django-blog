from django.urls import path

from . import views

app_name = "notifications"
urlpatterns = [
    path("settings/", views.settings, name="settings"),
]
