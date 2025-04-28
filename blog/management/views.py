import io
import json
import logging
from typing import Any, Optional

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .dataexport import get_all_data
from .dataimport import Data as ImportData
from .dataimport import DataError, FormError, data_from, load_all_data_in
from .forms import ExportDataForm, ImportDataForm

logger = logging.getLogger(__name__)


# Create your views here.
@staff_member_required
def data_console(request: HttpRequest) -> HttpResponse:
    import_form = ImportDataForm()
    export_form = ExportDataForm()
    return render(
        request,
        "blog/data_console.html",
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
@staff_member_required
@require_GET
def download_exported_file(request: HttpRequest) -> HttpResponse | FileResponse:
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


@staff_member_required
@require_POST
def handle_import_preview(request: HttpRequest) -> HttpResponse:
    data: Optional[ImportData] = None
    form: Optional[Any] = None

    try:
        data = data_from(request).ok_or_raise()
    except FormError as e:
        form = e.form
    except DataError as e:
        logger.error(e.e.errors())

        form = ImportDataForm(request.POST, request.FILES)
        form.add_error(
            "data_file",
            ValidationError("Unable to parse the file", code="format"),
        )

    return render(
        request,
        "blog/import_preview_fragment.html",
        {
            "data": data,
            "form": form,
        },
    )


@staff_member_required
@require_POST
def handle_import(request: HttpRequest) -> HttpResponse:
    try:
        data = data_from(request).ok_or_raise()
    except FormError as e:
        return HttpResponse(e)
    except DataError:
        return HttpResponse("<p>sommry, something went wrong</p>")

    posts, comments = load_all_data_in(data)
    return HttpResponse(
        "<p>import completed! {} posts, {} comments </p>".format(
            posts, comments
        )
    )
