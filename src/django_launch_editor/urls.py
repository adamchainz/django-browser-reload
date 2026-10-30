from __future__ import annotations

from django.urls import path

from django_launch_editor import views

app_name = "django_launch_editor"

urlpatterns = [
    path("launch/", views.launch, name="launch"),
]
