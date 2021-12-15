from django.urls import include, path

from example.core import views as core_views

urlpatterns = [
    path("", core_views.index),
    path("__reload__/", include("django_browser_reload.urls")),
]
