from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index_django(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "index.html",
        {
            "title": "Hello World",
        },
    )


def index_jinja(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "index.html",
        {
            "title": "Hello World",
        },
        using="jinja2",
    )
