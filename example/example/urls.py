from __future__ import annotations

from django.urls import include, path

from example import views

urlpatterns = [
    path("", views.index),
    path("__launch_editor__/", include("django_launch_editor.urls")),
]
