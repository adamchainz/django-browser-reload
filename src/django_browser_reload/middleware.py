from __future__ import annotations

import asyncio
import re
from typing import Any, Callable, Coroutine

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest
from django.http.response import HttpResponseBase

from django_browser_reload.jinja import django_browser_reload_script

insert_before_re = re.compile(r"</body>", flags=re.IGNORECASE)


class BrowserReloadMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        if not settings.DEBUG:
            raise MiddlewareNotUsed()

        self.get_response = get_response
        if asyncio.iscoroutinefunction(self.get_response):
            # Mark the class as async-capable, but do the actual switch
            # inside __call__ to avoid swapping out dunder methods
            self._is_coroutine = (
                asyncio.coroutines._is_coroutine  # type: ignore [attr-defined]
            )
        else:
            self._is_coroutine = None

    def __call__(
        self, request: HttpRequest
    ) -> HttpResponseBase | Coroutine[Any, Any, Any]:
        if self._is_coroutine:
            return self.__acall__(request)

        response = self.get_response(request)
        self.maybe_inject(response)
        return response

    async def __acall__(
        self, request: HttpRequest
    ) -> Coroutine[Any, Any, HttpResponseBase]:
        response = await self.get_response(request)
        self.maybe_inject(response)
        return response

    def maybe_inject(self, response: HttpResponseBase) -> None:
        if (
            not settings.DEBUG
            or getattr(response, "streaming", False)
            or response.get("Content-Encoding", "")
            or response.get("Content-Type", "").split(";", 1)[0] != "text/html"
        ):
            return

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
        if "Content-Length" in response:
            response["Content-Length"] = len(response.content)
