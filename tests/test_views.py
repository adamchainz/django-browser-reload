from __future__ import annotations

from http import HTTPStatus
from typing import Any
from unittest import mock

from django.core import signing
from django.test import Client, SimpleTestCase, override_settings
from launch_editor import LaunchEditorError

import tests.views
from django_launch_editor.tokens import SALT, make_token

URL = "/__launch_editor__/launch/"


@override_settings(DEBUG=True)
class LaunchTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.client = Client(enforce_csrf_checks=True)

    def post(self, data: dict[str, Any], csrf: bool = True) -> Any:
        headers = {}
        if csrf:
            headers["X-CSRFToken"] = "a" * 32
            self.client.cookies["csrftoken"] = "a" * 32
        return self.client.post(URL, data, headers=headers)

    @override_settings(DEBUG=False)
    def test_not_debug(self):
        response = self.post({"token": make_token(tests.views.__file__, 1)})

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get(self):
        response = self.client.get(URL)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_no_csrf_token(self):
        response = self.post({"token": make_token(tests.views.__file__, 1)}, csrf=False)

        assert response.status_code == HTTPStatus.FORBIDDEN

    @override_settings(MIDDLEWARE=[])
    def test_no_csrf_token_without_middleware(self):
        response = self.post({"token": make_token(tests.views.__file__, 1)}, csrf=False)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_missing_token(self):
        response = self.post({})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {
            "error": "Invalid or expired token. Reload the page and try again."
        }

    def test_unsigned_token(self):
        response = self.post({"token": "/etc/passwd"})

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_wrong_salt(self):
        token = signing.dumps([tests.views.__file__, 1])

        response = self.post({"token": token})

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_expired_token(self):
        with mock.patch("time.time", return_value=0):
            token = signing.dumps([tests.views.__file__, 1], salt=SALT)

        response = self.post({"token": token})

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_success(self):
        token = make_token(tests.views.__file__, 8)

        with mock.patch("django_launch_editor.views.launch_editor") as launch_editor:
            response = self.post({"token": token})

        assert response.status_code == HTTPStatus.NO_CONTENT
        launch_editor.assert_called_once_with(tests.views.__file__, 8)

    def test_launch_error(self):
        token = make_token(tests.views.__file__, 8)

        with mock.patch(
            "django_launch_editor.views.launch_editor",
            side_effect=LaunchEditorError("No editor"),
        ):
            response = self.post({"token": token})

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json() == {"error": "No editor"}


class MakeTokenTests(SimpleTestCase):
    def test_missing_file(self):
        assert make_token("/does/not/exist.py", 1) is None

    def test_directory(self):
        assert make_token("/", 1) is None
