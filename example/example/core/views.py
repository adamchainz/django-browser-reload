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


def favicon(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + '<text y=".9em" font-size="90">🔁</text>'
            + "</svg>"
        ),
        content_type="image/svg+xml",
    )
