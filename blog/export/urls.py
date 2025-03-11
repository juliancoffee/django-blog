from django.urls import path

from . import views

app_name = "management"
urlpatterns = [
    # export/import
    # TODO: make urls and names consistent
    path("data/", views.data_console, name="data-console"),
    path("export-file/", views.export_datafile, name="export_file"),
    path("import/", views.import_data, name="import"),
    path(
        "import-preview/",
        views.import_preview,
        name="import_preview",
    ),
]
