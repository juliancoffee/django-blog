from django.urls import path, re_path

import blog.auth.views
import blog.debug.views
import blog.post.views

app_name = "blog"
urlpatterns = [
    # post views
    # NOTE: if using regex, don't forget ^ to match from the begining
    # isn't strictly possible now, but I left it here just as an example
    re_path("^$|^index/", blog.post.views.index, name="index"),
    path("<int:post_id>/", blog.post.views.detail, name="detail"),
    path("<int:post_id>/comment/", blog.post.views.comment, name="comment"),
    # auth
    # TODO: that could be a separate Django app?
    path("accounts/login/", blog.auth.views.LoginView.as_view(), name="login"),
    path("accounts/logout/", blog.auth.views.instant_logout, name="logout"),
    path(
        "accounts/signup/", blog.auth.views.SignUpView.as_view(), name="signup"
    ),
    path("accounts/profile/", blog.auth.views.profile, name="profile"),
    # misc
    path("debug_view/", blog.debug.views.debug_view, name="debug_view"),
]
