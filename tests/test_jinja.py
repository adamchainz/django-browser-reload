from __future__ import annotations

from django.test import override_settings
from django.test import SimpleTestCase

from django_browser_reload.jinja import django_browser_reload_script


class DjangoBrowserReloadScriptTests(SimpleTestCase):
    def test_non_debug_empty(self):
        result = django_browser_reload_script()

        assert result == ""

    def test_debug_success(self):
        with override_settings(DEBUG=True):
            result = django_browser_reload_script()

        assert result == (
            '<script src="/static/django-browser-reload/reload-listener.js"'
            + ' data-worker-script-path="/static/django-browser-reload/'
            + 'reload-worker.js"'
            + ' data-events-path="/__reload__/events/" defer></script>'
        )
