from __future__ import annotations

import re
from collections.abc import Awaitable
from typing import Callable

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase

from django_browser_reload.jinja import django_browser_reload_script

insert_before_re = re.compile(r"</body>", flags=re.IGNORECASE)


class BrowserReloadMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(
        self,
        get_response: (
            Callable[[HttpRequest], HttpResponseBase]
            | Callable[[HttpRequest], Awaitable[HttpResponseBase]]
        ),
    ) -> None:
        if not settings.DEBUG:
            raise MiddlewareNotUsed()

        self.get_response = get_response
        self.async_mode = iscoroutinefunction(self.get_response)

        if self.async_mode:
            # Mark the class as async-capable, but do the actual switch
            # inside __call__ to avoid swapping out dunder methods
            markcoroutinefunction(self)

    def __call__(
        self, request: HttpRequest
    ) -> HttpResponseBase | Awaitable[HttpResponseBase]:
        if self.async_mode:
            return self.__acall__(request)

        response = self.get_response(request)
        assert isinstance(response, HttpResponseBase)
        self.maybe_inject(response)
        return response

    async def __acall__(self, request: HttpRequest) -> HttpResponseBase:
        result = self.get_response(request)
        assert not isinstance(result, HttpResponseBase)  # type narrow
        response = await result
        self.maybe_inject(response)
        return response

    def maybe_inject(self, response: HttpResponseBase) -> None:
        if (
            not settings.DEBUG
            or getattr(response, "streaming", False)
            or response.headers.get("content-encoding", "")
            or response.headers.get("content-type", "").split(";", 1)[0] != "text/html"
        ):
            return

        assert isinstance(response, HttpResponse)
        content = response.content.decode(response.charset)
        # Find last match
        found = False
        for match in insert_before_re.finditer(content):  # noqa: B007
            found = True
        if not found:
            return

        head = content[: match.start()]
        tag = match[0]
        tail = content[match.end() :]

        response.content = head + django_browser_reload_script() + tag + tail
        if "content-length" in response.headers:
            response["content-length"] = len(response.content)
