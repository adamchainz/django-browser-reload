from django.urls import include, path

from example.core import views as core_views

urlpatterns = [
    path("", core_views.index),
    path("__debug__/", include("django_browser_reload.urls")),
]
