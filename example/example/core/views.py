from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index_django(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "index.html",
        {
            "title": "My Awesome Site",
        },
    )


def index_jinja(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "index.html",
        {
            "title": "My Awesome Site",
        },
        using="jinja2",
    )
