from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
]
