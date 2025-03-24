from __future__ import annotations

import time
from http import HTTPStatus
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.http import StreamingHttpResponse
from django.middleware.gzip import GZipMiddleware
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.test import override_settings
from django.utils.autoreload import BaseReloader

import django_browser_reload
from django_browser_reload import views
from tests.compat import aiter
from tests.compat import anext


class OnAutoreloadStartedTests(SimpleTestCase):
    def test_success(self):
        calls: list[tuple[Path, str]] = []

        class FakeReloader(BaseReloader):
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


class HandleSigingTests(SimpleTestCase):
    def test_handle_sigint(self):
        views.handle_sigint(0, None)
        assert views.should_exit_event.is_set()
        views.should_exit_event.clear()


@override_settings(DEBUG=True)
class EventsTests(SimpleTestCase):
    def setUp(self):
        views.should_exit_event.clear()

    @override_settings(DEBUG=False)
    def test_fail_not_debug(self):
        response = self.client.get("/__reload__/events/")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_fail_not_accepted(self):
        response = self.client.get(
            "/__reload__/events/", headers={"accept": "text/html"}
        )

        assert response.status_code == HTTPStatus.NOT_ACCEPTABLE

    def test_success_ping(self):
        response = self.client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "text/event-stream"
        response_iterable = iter(response)
        event = next(response_iterable)
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
        assert response.headers["content-type"] == "text/event-stream"
        response_iterable = iter(response)
        event1 = next(response_iterable)
        event2 = next(response_iterable)
        assert event1 == event2

    def test_success_template_change(self):
        response = self.client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)
        views.should_reload_event.set()

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "text/event-stream"
        response_iterable = iter(response)
        # Skip version ID message
        next(response_iterable)
        event = next(response_iterable)
        assert event == b'data: {"type": "reload"}\n\n'
        assert not views.should_reload_event.is_set()

    def test_success_template_change_with_gzip(self):
        middleware = GZipMiddleware(views.events)
        request = RequestFactory(headers={"accept-encoding": "gzip"}).get("/")
        response = middleware(request)
        assert isinstance(response, StreamingHttpResponse)
        views.should_reload_event.set()

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "text/event-stream"
        assert response.headers["content-encoding"] == ""
        response_iterable = iter(response)
        # Skip version ID message
        next(response_iterable)
        event = next(response_iterable)
        assert event == b'data: {"type": "reload"}\n\n'
        assert not views.should_reload_event.is_set()

    def test_close_connection_on_should_close_set(self):
        response = self.client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "text/event-stream"
        response_iterable = iter(response)

        # Set the should_exit_event
        views.should_exit_event.set()

        # The the iteration should stop
        with self.assertRaises(StopIteration):
            next(response_iterable)


@override_settings(DEBUG=True)
class AsyncEventsTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    async def test_fail_not_debug(self):
        response = await self.async_client.get("/__reload__/events/")

        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_fail_not_accepted(self):
        response = await self.async_client.get(
            "/__reload__/events/", ACCEPT="text/html"
        )

        assert response.status_code == HTTPStatus.NOT_ACCEPTABLE

    async def test_success_ping(self):
        response = await self.async_client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "text/event-stream"

        event = await anext(aiter(response))
        assert event == (
            b'data: {"type": "ping", "versionId": "'
            + views.version_id.encode()
            + b'"}\n\n'
        )

    @mock.patch.object(views, "PING_DELAY", 0.001)
    async def test_success_ping_twice(self):
        response = await self.async_client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "text/event-stream"
        response_iter = aiter(response)
        event1 = await anext(response_iter)
        event2 = await anext(response_iter)
        assert event1 == event2

    async def test_success_template_change(self):
        response = await self.async_client.get("/__reload__/events/")
        assert isinstance(response, StreamingHttpResponse)
        views.should_reload_event.set()

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "text/event-stream"
        response_iter = aiter(response)
        # Skip version ID message
        await anext(response_iter)
        event = await anext(response_iter)
        assert event == b'data: {"type": "reload"}\n\n'
        assert not views.should_reload_event.is_set()
