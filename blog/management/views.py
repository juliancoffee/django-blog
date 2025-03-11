import io
import json
import logging

from django.contrib.auth.decorators import user_passes_test
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render

from blog.utils import user_is_staff_check

from .dataexport import get_all_data
from .dataimport import load_all_data_in, parse_import_data
from .forms import ExportDataForm, ImportDataForm

logger = logging.getLogger(__name__)


# Create your views here.
@user_passes_test(user_is_staff_check)
def data_console(request: HttpRequest) -> HttpResponse:
    import_form = ImportDataForm()
    export_form = ExportDataForm()
    return render(
        request,
        "blog/export_page.html",
        {
            "import_form": import_form,
            "export_form": export_form,
        },
    )


# NOTE: It's a GET request, but we're safe.
#
# The only case where this might be a problem is if another browser makes
# a fetch request behind the scenes, but CORS policies wouldn't allow that.
#
# - If you just visit this page via browser, that's completely fine, we will
# check authentication and authorization server-side.
# - If you visit this page with something like a `curl`, you simply won't pass
# auth.
@user_passes_test(user_is_staff_check)
def export_datafile(request: HttpRequest) -> HttpResponse | FileResponse:
    # TODO: this should probably have some filtering and stuff, because we're
    # practically loading our whole database into memory at once, but whatever.
    #
    # For now, my blog doesn't have any users except me, really, so it's ok.
    databuff = io.BytesIO()
    data = get_all_data()

    # I couldn't get json output the data into the buffer, mypy was mad at me.
    #
    # It is happy with this code although it's probably less efficient.
    databuff.write(json.dumps(data).encode())
    # NOTE: don't forget to seek to the beginning
    databuff.seek(0)

    return FileResponse(
        databuff,
        as_attachment="download" in request.GET,
        filename="data.json",
    )


@user_passes_test(user_is_staff_check)
def import_preview(request: HttpRequest) -> HttpResponse:
    data = parse_import_data(request)
    return render(request, "blog/import_preview_fragment.html", {"data": data})


@user_passes_test(user_is_staff_check)
def import_data(request: HttpRequest) -> HttpResponse:
    counters = None
    try:
        counters = load_all_data_in(request)
    except Exception:
        logger.error("failed to import the data", exc_info=True)

    if counters is not None:
        posts, comments = counters
        return HttpResponse(
            "<p>import completed! {} posts, {} comments </p>".format(
                posts, comments
            )
        )
    else:
        return HttpResponse("<p>sommry, something went wrong</p>")
