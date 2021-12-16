import json
import threading
from http import HTTPStatus
from pathlib import Path
from typing import Any, Generator

import django
from django.conf import settings
from django.dispatch import receiver
from django.http import Http404, HttpRequest, HttpResponse, StreamingHttpResponse
from django.http.response import HttpResponseBase
from django.utils.autoreload import file_changed
from django.utils.crypto import get_random_string

# For detecting when Python has reloaded, use a random version ID in memory.
# When the worker receives a different version from the one it saw previously,
# it reloads.
version_id = get_random_string(32)

# Communicate template changes to the running polls thread
should_reload_event = threading.Event()


# Signal receiver connected in AppConfig.ready()
if django.VERSION >= (3, 2):
    from django.template.autoreload import get_template_directories

    @receiver(file_changed)
    def template_changed(*, file_path: Path, **kwargs: Any) -> None:
        for template_dir in get_template_directories():
            if template_dir in file_path.parents:
                should_reload_event.set()
                break


def message(type_: str, **kwargs: Any) -> bytes:
    """
    Encode an event stream message.

    We distinguish message types with a 'type' inside the 'data' field, rather
    than the 'message' field, to allow the worker to process all messages with
    a single event listener.
    """
    jsonified = json.dumps({"type": type_, **kwargs})
    return f"data: {jsonified}\n\n".encode()


PING_DELAY = 1.0  # seconds


def events(request: HttpRequest) -> HttpResponseBase:
    if not settings.DEBUG:
        raise Http404()

    if django.VERSION >= (3, 1) and not request.accepts("text/event-stream"):
        return HttpResponse(status=HTTPStatus.NOT_ACCEPTABLE)

    def event_stream() -> Generator[bytes, None, None]:
        while True:
            yield message("ping", versionId=version_id)

            should_reload = should_reload_event.wait(timeout=PING_DELAY)
            if should_reload:
                should_reload_event.clear()
                yield message("reload")

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
