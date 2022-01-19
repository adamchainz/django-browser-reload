from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
]
