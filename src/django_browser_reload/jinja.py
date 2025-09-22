from __future__ import annotations

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html


def django_browser_reload_script(nonce: str | None = None) -> str:
    if not settings.DEBUG:
        return ""
    if nonce:
        return format_html(
            (
                '<script src="{}"'
                + ' data-worker-script-path="{}"'
                + ' data-events-path="{}"'
                + ' defer nonce="{}"></script>'
            ),
            static("django-browser-reload/reload-listener.js"),
            static("django-browser-reload/reload-worker.js"),
            reverse("django_browser_reload:events"),
            nonce,
        )
    else:
        return format_html(
            (
                '<script src="{}"'
                + ' data-worker-script-path="{}"'
                + ' data-events-path="{}"'
                + " defer></script>"
            ),
            static("django-browser-reload/reload-listener.js"),
            static("django-browser-reload/reload-worker.js"),
            reverse("django_browser_reload:events"),
        )
