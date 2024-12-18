from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:post_id>/", views.detail, name="detail"),
    path("<int:post_id>/comment/", views.comment, name="comment"),
    path("debug_view", views.debug_view, name="debug_view"),
]
