from __future__ import annotations

from django.apps import AppConfig


class DjangoBrowserReloadAppConfig(AppConfig):
    name = "django_browser_reload"
    verbose_name = "django-browser-reload"

    def ready(self) -> None:
        # Ensure signal always connected
        from django_browser_reload import views  # noqa
