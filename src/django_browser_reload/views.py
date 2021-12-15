import json
from pathlib import Path
from threading import Event
from typing import Any, Generator

import django
from django.dispatch import receiver
from django.http import HttpRequest, StreamingHttpResponse
from django.utils.autoreload import file_changed
from django.utils.crypto import get_random_string

# For detecting when Python has reloaded, use a random version ID in memory.
# When the worker receives a different version from the one it saw previously,
# it reloads.
version_id = get_random_string(32)

# Communicate template changes to the running polls thread
template_changed_event = Event()


# Signal receiver connected in AppConfig.ready()
if django.VERSION >= (3, 2):
    from django.template.autoreload import get_template_directories

    @receiver(file_changed)
    def template_changed(*, file_path: Path, **kwargs: Any) -> None:
        for template_dir in get_template_directories():
            if template_dir in file_path.parents:
                template_changed_event.set()


def message(type_: str, **kwargs: Any) -> bytes:
    jsonified = json.dumps({"type": type_, **kwargs})
    return f"data: {jsonified}\n\n".encode()


PING_DELAY = 1.0  # seconds


def events(request: HttpRequest) -> StreamingHttpResponse:
    def event_stream() -> Generator[bytes, None, None]:
        while True:
            yield message("ping", versionId=version_id)

            template_changed = template_changed_event.wait(timeout=PING_DELAY)
            if template_changed:
                template_changed_event.clear()
                yield message("templateChange")

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
