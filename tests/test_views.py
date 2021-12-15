from http import HTTPStatus
from pathlib import Path
from unittest import mock

import django
import pytest
from django.conf import settings
from django.test import SimpleTestCase, override_settings

from django_browser_reload import views

django_3_1_plus = pytest.mark.skipif(
    django.VERSION < (3, 1), reason="Requires Django 3.1+"
)
django_3_2_plus = pytest.mark.skipif(
    django.VERSION < (3, 2), reason="Requires Django 3.2+"
)


@django_3_2_plus
class TemplateChangedTests(SimpleTestCase):
    def test_ignored(self):
        views.template_changed(file_path=Path("/tmp/nothing"))

        assert not views.template_changed_event.is_set()

    def test_success(self):
        path = settings.BASE_DIR / "templates" / "example.html"

        views.template_changed(file_path=path)

        assert views.template_changed_event.is_set()
        views.template_changed_event.clear()


@override_settings(DEBUG=True)
class EventsTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_fail_not_debug(self):
        response = self.client.get("/__reload__/events/")

        assert response.status_code == HTTPStatus.NOT_FOUND

    @django_3_1_plus
    def test_fail_not_accepted(self):
        response = self.client.get("/__reload__/events/", HTTP_ACCEPT="text/html")

        assert response.status_code == HTTPStatus.NOT_ACCEPTABLE

    def test_success_ping(self):
        response = self.client.get("/__reload__/events/")

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

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/event-stream"
        event1 = next(response.streaming_content)
        event2 = next(response.streaming_content)
        assert event1 == event2

    def test_success_template_change(self):
        response = self.client.get("/__reload__/events/")
        views.template_changed_event.set()

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "text/event-stream"
        # Skip version ID message
        next(response.streaming_content)
        event = next(response.streaming_content)
        assert event == b'data: {"type": "templateChange"}\n\n'
        assert not views.template_changed_event.is_set()
