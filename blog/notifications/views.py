from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.


def settings(request: HttpRequest) -> HttpResponse:
    return render(request, "blog/notif_settings.html")
