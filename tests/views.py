from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def error(request: HttpRequest) -> HttpResponse:
    raise ValueError("Oh no")


def template_error(request: HttpRequest) -> HttpResponse:
    return render(request, "error.html")
