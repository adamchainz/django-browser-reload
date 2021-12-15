from django.apps import AppConfig
from django.dispatch import receiver
from django.utils.autoreload import file_changed

from django_browser_reload.views import template_changed


class DjangoBrowserReloadAppConfig(AppConfig):
    name = "django_browser_reload"
    verbose_name = "django-browser-reload"

    def ready(self) -> None:
        receiver(file_changed)(template_changed)
