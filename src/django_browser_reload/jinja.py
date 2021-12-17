from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html


def django_browser_reload_script() -> str:
    if not settings.DEBUG:
        return ""
    return format_html(
        (
            '<script src="{}"'
            + ' data-worker-script-path="{}"'
            + ' data-events-path="{}"'
            + " async></script>"
        ),
        static("django-browser-reload/reload-listener.js"),
        static("django-browser-reload/reload-worker.js"),
        reverse("django_browser_reload:events"),
    )
