from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "index.html",
        {
            "title": "Hello World",
        },
    )
