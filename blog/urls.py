from django.urls import include, path, re_path

import blog.views

app_name = "blog"
urlpatterns = [
    # post views
    re_path(
        # NOTE: if using regex, don't forget ^ to match from the begining
        # isn't strictly possible now, but I left it here just as an example
        "^$|^index/",
        blog.views.index,
        name="index",
    ),
    path("handle_post/", blog.views.PostView.as_view(), name="handle_post"),
    # comment views
    path("<int:post_id>/", blog.views.detail, name="detail"),
    path(
        "<int:post_id>/handle_comment/",
        blog.views.CommentView.as_view(),
        name="handle_comment",
    ),
    # auth
    path("accounts/", include("blog.accounts.urls")),
    # notifications
    path("notifications/", include("blog.notifications.urls")),
    # export/import
    path("management/", include("blog.management.urls")),
    # misc
    path("devmode/", include("blog.devmode.urls")),
]
