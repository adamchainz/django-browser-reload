from __future__ import annotations

from django.apps import AppConfig
from django.core import checks

from .checks import check_django_browser_reload_setup


class DjangoBrowserReloadAppConfig(AppConfig):
    name = "django_browser_reload"
    verbose_name = "django-browser-reload"

    def ready(self) -> None:
        # Ensure signal always connected
        from django_browser_reload import views  # noqa
        checks.register(check_django_browser_reload_setup, checks.Tags.compatibility)
