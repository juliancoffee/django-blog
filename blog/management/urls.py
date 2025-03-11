from django.urls import path

from . import views

app_name = "management"
urlpatterns = [
    # export/import
    path("data/", views.data_console, name="data_console"),
    # export
    path(
        "export-file/",
        views.download_exported_file,
        name="download_exported_file",
    ),
    # import
    path("import/", views.handle_import, name="handle_import"),
    path(
        "import-preview/",
        views.handle_import_preview,
        name="handle_import_preview",
    ),
]
