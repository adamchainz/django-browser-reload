from __future__ import annotations

from django.urls import include
from django.urls import path

from example.core import views as core_views

urlpatterns = [
    path("", core_views.index_django),
    path("jinja/", core_views.index_jinja),
    path("favicon.ico", core_views.favicon),
    path("__reload__/", include("django_browser_reload.urls")),
]
