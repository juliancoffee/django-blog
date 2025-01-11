from django.urls import path, re_path

import blog.auth.views
import blog.debug.views
import blog.post.views

app_name = "blog"
urlpatterns = [
    # post views
    # NOTE: if using regex, don't forget ^ to match from the begining
    re_path("^$|^index/", blog.post.views.index, name="index"),
    path("<int:post_id>/", blog.post.views.detail, name="detail"),
    path("<int:post_id>/comment/", blog.post.views.comment, name="comment"),
    # auth
    # TODO: that could be a separate Django app?
    path("accounts/login/", blog.auth.views.LoginView.as_view(), name="login"),
    path("accounts/logout/", blog.auth.views.instant_logout, name="logout"),
    # misc
    path("debug_view/", blog.debug.views.debug_view, name="debug_view"),
]
