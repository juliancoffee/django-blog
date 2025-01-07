from django.urls import path

import blog.debug.views
import blog.post.views

app_name = "blog"
urlpatterns = [
    path("", blog.post.views.index, name="index"),
    path("<int:post_id>/", blog.post.views.detail, name="detail"),
    path("<int:post_id>/comment/", blog.post.views.comment, name="comment"),
    path("debug_view", blog.debug.views.debug_view, name="debug_view"),
]
