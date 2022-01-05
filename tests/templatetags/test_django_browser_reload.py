from django.template import Context, Template
from django.test import SimpleTestCase, override_settings


class DjangoBrowserReloadScriptTests(SimpleTestCase):
    def test_non_debug_empty(self):
        result = Template(
            "{% load django_browser_reload %}{% django_browser_reload_script %}"
        ).render(Context())

        assert result == ""

    def test_debug_success(self):
        with override_settings(DEBUG=True):
            result = Template(
                "{% load django_browser_reload %}{% django_browser_reload_script %}"
            ).render(Context())

        assert result == (
            '<script src="/static/django-browser-reload/reload-listener.js"'
            + ' data-worker-script-path="/static/django-browser-reload/'
            + 'reload-worker.js"'
            + ' data-events-path="/__reload__/events/" defer></script>'
        )
