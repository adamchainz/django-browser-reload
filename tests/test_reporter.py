from __future__ import annotations

import json
import re
import sys
from typing import Any

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, override_settings

import tests.views
from django_launch_editor.reporter import LaunchEditorExceptionReporter
from django_launch_editor.tokens import load_token


def get_config(html: str) -> dict[str, Any]:
    match = re.search(
        r'<script id="django-launch-editor-data" type="application/json">(.*?)</script>',
        html,
    )
    assert match is not None
    return json.loads(match[1])  # type: ignore [no-any-return]


def make_reporter(**kwargs: Any) -> LaunchEditorExceptionReporter:
    request = kwargs.pop("request", RequestFactory().get("/"))
    try:
        exec("raise ValueError('Oh no')")
    except ValueError:
        exc_type, exc_value, tb = sys.exc_info()
    return LaunchEditorExceptionReporter(request, exc_type, exc_value, tb, **kwargs)


@override_settings(DEBUG=True)
class LaunchEditorExceptionReporterTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.client = self.client_class(raise_request_exception=False)

    def test_error_page(self):
        response = self.client.get("/error/")

        assert response.status_code == 500
        html = response.text
        assert html.index('id="django-launch-editor-data"') < html.index("</body>")
        assert "<script>(function () {" in html
        config = get_config(html)
        assert config["url"] == "/__launch_editor__/launch/"
        assert config["csrfToken"]
        assert config["template"] is None
        assert len(config["frames"]) >= 2
        filename, line = load_token(config["frames"][-1])
        assert filename == tests.views.__file__
        assert line == 8

    def test_csrf_cookie_set(self):
        response = self.client.get("/error/")

        assert "csrftoken" in response.cookies

    def test_template_error(self):
        response = self.client.get("/template-error/")

        assert response.status_code == 500
        config = get_config(response.text)
        filename, line = load_token(config["template"])
        assert filename == str(settings.BASE_DIR / "templates" / "error.html")
        assert line == 2

    def test_frame_without_file(self):
        reporter = make_reporter()

        config = get_config(reporter.get_traceback_html())

        # The frame for exec()’d code has no file.
        assert config["frames"][-1] is None
        assert config["frames"][0] is not None

    def test_no_traceback(self):
        reporter = LaunchEditorExceptionReporter(
            RequestFactory().get("/"), None, None, None
        )

        config = get_config(reporter.get_traceback_html())

        assert config["frames"] == []

    @override_settings(DEBUG=False)
    def test_not_debug(self):
        html = make_reporter().get_traceback_html()

        assert "django-launch-editor" not in html
        assert "</body>" in html

    def test_email(self):
        html = make_reporter(is_email=True).get_traceback_html()

        assert "django-launch-editor" not in html

    def test_no_request(self):
        html = make_reporter(request=None).get_traceback_html()

        assert "django-launch-editor" not in html

    @override_settings(ROOT_URLCONF="tests.urls_without_launch_editor")
    def test_url_not_installed(self):
        response = self.client.get("/error/")

        assert response.status_code == 500
        assert "django-launch-editor" not in response.text

    def test_no_body_end(self):
        class NoBodyReporter(LaunchEditorExceptionReporter):
            @property
            def html_template_path(self):
                return settings.BASE_DIR / "templates" / "no_body.html"

        reporter = NoBodyReporter(RequestFactory().get("/"), None, None, None)

        html = reporter.get_traceback_html()

        assert "django-launch-editor" not in html
