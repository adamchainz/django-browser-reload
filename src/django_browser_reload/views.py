import json
from pathlib import Path
from threading import Event
from typing import Any, Generator

from django.http import HttpRequest, StreamingHttpResponse
from django.template.autoreload import get_template_directories
from django.utils.crypto import get_random_string

# For detecting when Python has reloaded, use a random “version” in memory.
# When the worker receives a different version from the one it saw previously,
# it reloads.
current_version = get_random_string(length=32)

# Communicate template changes to the running polls thread
template_changed_event = Event()


# Signal receiver connected in AppConfig.ready()
def template_changed(*, file_path: Path, **kwargs: Any) -> None:
    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            template_changed_event.set()


def message(type_: str, **kwargs: Any) -> bytes:
    jsonified = json.dumps({"type": type_, **kwargs})
    return f"data: {jsonified}\n\n".encode()


def events(request: HttpRequest) -> StreamingHttpResponse:
    def event_stream() -> Generator[bytes, None, None]:
        while True:
            yield message("version", version=current_version)

            template_changed = template_changed_event.wait(timeout=1.0)
            if template_changed:
                template_changed_event.clear()
                yield message("templateChange")

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
