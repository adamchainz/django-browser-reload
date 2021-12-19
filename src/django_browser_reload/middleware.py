import re
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from django_browser_reload.jinja import django_browser_reload_script

insert_before_re = re.compile(r"</body>", flags=re.IGNORECASE)


class BrowserReloadMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if (
            not settings.DEBUG
            or getattr(response, "streaming", False)
            or response.get("Content-Encoding", "")
            or response.get("Content-Type", "").split(";", 1)[0] != "text/html"
        ):
            return response

        content = response.content.decode(response.charset)
        # Find last match
        found = False
        for match in insert_before_re.finditer(content):  # noqa: B007
            found = True
        if not found:
            return response

        head = content[: match.start()]
        tag = match[0]
        tail = content[match.end() :]

        response.content = head + django_browser_reload_script() + tag + tail
        if "Content-Length" in response:
            response["Content-Length"] = len(response.content)

        return response
