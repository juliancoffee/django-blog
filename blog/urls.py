from django.urls import include, path, re_path

import blog.debug.views
import blog.export.views
import blog.views

app_name = "blog"
urlpatterns = [
    # post views
    # NOTE: if using regex, don't forget ^ to match from the begining
    # isn't strictly possible now, but I left it here just as an example
    re_path("^$|^index/", blog.views.index, name="index"),
    path("<int:post_id>/", blog.views.detail, name="detail"),
    path(
        "<int:post_id>/comment/",
        blog.views.CommentView.as_view(),
        name="comment",
    ),
    # auth
    path("accounts/", include("blog.accounts.urls")),
    # export/import
    path("data_management/", blog.export.views.export_page, name="export_page"),
    path("export-file/", blog.export.views.export_datafile, name="export_file"),
    path("import/", blog.export.views.import_data, name="import"),
    path(
        "import_preview/",
        blog.export.views.import_preview,
        name="import_preview",
    ),
    # misc
    path("debug_view/", blog.debug.views.debug_view, name="debug_view"),
]
