from django.urls import path

from . import views

app_name = "devmode"
urlpatterns = [
    path("spylog/", views.spylog, name="spylog"),
]
