from __future__ import annotations

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http.response import HttpResponseBase
from django.test import override_settings
from django.test import RequestFactory
from django.test import SimpleTestCase

from django_browser_reload.middleware import BrowserReloadMiddleware


@override_settings(DEBUG=True)
class BrowserReloadMiddlewareTests(SimpleTestCase):
    request_factory = RequestFactory()

    def setUp(self):
        self.request = self.request_factory.get("/")
        self.response: HttpResponseBase = HttpResponse("<html><body></body></html>")

        def get_response(request: HttpRequest) -> HttpResponseBase:
            return self.response

        self.middleware = BrowserReloadMiddleware(get_response)

    @override_settings(DEBUG=False)
    def test_not_debug_instantiation(self):
        with self.assertRaises(MiddlewareNotUsed):
            BrowserReloadMiddleware(self.middleware.get_response)

    @override_settings(DEBUG=False)
    def test_not_debug(self):
        response = self.middleware(self.request)

        assert isinstance(response, HttpResponse)
        assert response.content == b"<html><body></body></html>"

    def test_streaming_response(self):
        # content that the middleware could inject in if it supported streaming
        # responses
        content_iter = iter(["<html><body>", "</body></html>"])
        self.response = StreamingHttpResponse(content_iter)

        response = self.middleware(self.request)

        assert isinstance(response, StreamingHttpResponse)
        content = b"".join(response.streaming_content)
        assert content == b"<html><body></body></html>"

    def test_encoded_response(self):
        self.response["Content-Encoding"] = "zabble"

        response = self.middleware(self.request)

        assert isinstance(response, HttpResponse)
        assert response.content == b"<html><body></body></html>"

    def test_text_response(self):
        self.response["Content-Type"] = "text/plain"

        response = self.middleware(self.request)

        assert isinstance(response, HttpResponse)
        assert response.content == b"<html><body></body></html>"

    def test_no_match(self):
        self.response = HttpResponse("<html><body>Woops")

        response = self.middleware(self.request)

        assert isinstance(response, HttpResponse)
        assert response.content == b"<html><body>Woops"

    def test_success(self):
        self.response = HttpResponse("<html><body></body></html>")
        self.response["Content-Length"] = len(self.response.content)

        response = self.middleware(self.request)

        assert isinstance(response, HttpResponse)
        assert response.content == (
            b"<html><body>"
            + b'<script src="/static/django-browser-reload/reload-listener.js"'
            + b' data-worker-script-path="/static/django-browser-reload/'
            + b'reload-worker.js"'
            + b' data-events-path="/__reload__/events/" defer></script>'
            + b"</body></html>"
        )

    async def test_async_success(self):
        async def get_response(request: HttpRequest) -> HttpResponse:
            return HttpResponse("<html><body></body></html>")

        middleware = BrowserReloadMiddleware(get_response)

        result = middleware(self.request)
        assert not isinstance(result, HttpResponseBase)
        response = await result

        assert isinstance(response, HttpResponse)
        assert response.content == (
            b"<html><body>"
            + b'<script src="/static/django-browser-reload/reload-listener.js"'
            + b' data-worker-script-path="/static/django-browser-reload/'
            + b'reload-worker.js"'
            + b' data-events-path="/__reload__/events/" defer></script>'
            + b"</body></html>"
        )

    def test_multipart_content_type(self):
        self.response["Content-Type"] = "text/html; thingy=that; charset=utf-8"

        response = self.middleware(self.request)

        assert isinstance(response, HttpResponse)
        assert response.content == (
            b"<html><body>"
            + b'<script src="/static/django-browser-reload/reload-listener.js"'
            + b' data-worker-script-path="/static/django-browser-reload/'
            + b'reload-worker.js"'
            + b' data-events-path="/__reload__/events/" defer></script>'
            + b"</body></html>"
        )

    def test_two_matches(self):
        self.response = HttpResponse("<html><body></body><body></body></html>")

        response = self.middleware(self.request)

        assert isinstance(response, HttpResponse)
        assert response.content == (
            b"<html><body></body><body>"
            + b'<script src="/static/django-browser-reload/reload-listener.js"'
            + b' data-worker-script-path="/static/django-browser-reload/'
            + b'reload-worker.js"'
            + b' data-events-path="/__reload__/events/" defer></script>'
            + b"</body></html>"
        )
