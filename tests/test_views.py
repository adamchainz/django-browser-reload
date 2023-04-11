from __future__ import annotations

import time
from http import HTTPStatus
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.http import StreamingHttpResponse
from django.middleware.gzip import GZipMiddleware
from django.test import override_settings
from django.test import RequestFactory
from django.test import SimpleTestCase

import django_browser_reload
from django_browser_reload import views


class OnAutoreloadStartedTests(SimpleTestCase):
    def test_success(self):
        calls: list[tuple[Path, str]] = []

        class FakeReloader:
            def watch_dir(self, directory, glob):
                calls.append((directory, glob))

        reloader = FakeReloader()

        views.on_autoreload_started(sender=reloader)

        assert calls == [
            (settings.BASE_DIR / "templates" / "jinja", "**/*"),
            (settings.BASE_DIR / "static", "**/*"),
            (Path(django_browser_reload.__file__).parent / "static", "**/*"),
        ]


class OnFileChangedTests(SimpleTestCase):
    def test_ignored(self):
        views.on_file_changed(file_path=Path("/tmp/nothing"))

        time.sleep(views.RELOAD_DEBOUNCE_TIME * 1.1)
        assert not views.should_reload_event.is_set()

    def test_django_template(self):
        path = settings.BASE_DIR / "templates" / "django" / "example.html"

        result = views.on_file_changed(file_path=path)

        time.sleep(views.RELOAD_DEBOUNCE_TIME * 1.1)
        assert result is True
        assert views.should_reload_event.is_set()
        views.should_reload_event.clear()

    def test_jinja_template(self):
        path = settings.BASE_DIR / "templates" / "jinja" / "example.html"

        result = views.on_file_changed(file_path=path)

        time.sleep(views.RELOAD_DEBOUNCE_TIME * 1.1)
        assert result is True
        assert views.should_reload_event.is_set()
        views.should_reload_event.clear()

    def test_static_asset(self):
        path = settings.BASE_DIR / "static" / "example.css"

        result = views.on_file_changed(file_path=path)

        time.sleep(views.RELOAD_DEBOUNCE_TIME * 1.1)
        assert result is True
        assert views.should_reload_event.is_set()
        views.should_reload_event.clear()


@override_settings(DEBUG=True)
class EventsTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_fail_not_debug(self):
        response = self.client.get("/__reload__/events/")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_fail_not_accepted(self):
        response = self.client.get("/__reload__/events/", HTTP_ACCEPT="text/html")

        assert response.status_code == HTTPStatus.NOT_ACCEPTABLE

    def test_success_ping(self):
        response = self.client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/event-stream"
        event = next(response.streaming_content)
        assert event == (
            b'data: {"type": "ping", "versionId": "'
            + views.version_id.encode()
            + b'"}\n\n'
        )

    @mock.patch.object(views, "PING_DELAY", 0.001)
    def test_success_ping_twice(self):
        response = self.client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/event-stream"
        event1 = next(response.streaming_content)
        event2 = next(response.streaming_content)
        assert event1 == event2

    def test_success_template_change(self):
        response = self.client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)
        views.should_reload_event.set()

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/event-stream"
        # Skip version ID message
        next(response.streaming_content)
        event = next(response.streaming_content)
        assert event == b'data: {"type": "reload"}\n\n'
        assert not views.should_reload_event.is_set()

    def test_success_template_change_with_gzip(self):
        # https://github.com/typeddjango/django-stubs/pull/1421
        middleware = GZipMiddleware(views.events)  # type: ignore[arg-type]
        request = RequestFactory(HTTP_ACCEPT_ENCODING="gzip").get("/")
        response = middleware(request)
        assert isinstance(response, StreamingHttpResponse)
        views.should_reload_event.set()

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/event-stream"
        assert response["Content-Encoding"] == ""
        # Skip version ID message
        next(response.streaming_content)
        event = next(response.streaming_content)
        assert event == b'data: {"type": "reload"}\n\n'
        assert not views.should_reload_event.is_set()
