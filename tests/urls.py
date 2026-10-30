from __future__ import annotations

from django.urls import include, path

from tests import views

urlpatterns = [
    path("__launch_editor__/", include("django_launch_editor.urls")),
    path("error/", views.error),
    path("template-error/", views.template_error),
]
