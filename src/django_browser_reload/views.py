import json
import threading
from http import HTTPStatus
from pathlib import Path
from typing import Any, Generator, Optional, Set

import django
from django.conf import settings
from django.contrib.staticfiles.finders import (
    AppDirectoriesFinder,
    FileSystemFinder,
    get_finders,
)
from django.dispatch import receiver
from django.http import Http404, HttpRequest, HttpResponse, StreamingHttpResponse
from django.http.response import HttpResponseBase
from django.template import engines
from django.template.backends.base import BaseEngine
from django.utils.autoreload import BaseReloader, autoreload_started, file_changed
from django.utils.crypto import get_random_string

if django.VERSION >= (3, 2):
    from django.template.autoreload import (
        get_template_directories as django_template_directories,
    )

    HAVE_DJANGO_TEMPLATE_DIRECTORIES = True
else:
    HAVE_DJANGO_TEMPLATE_DIRECTORIES = False

# For detecting when Python has reloaded, use a random version ID in memory.
# When the worker receives a different version from the one it saw previously,
# it reloads.
version_id = get_random_string(32)

# Communicate template changes to the running polls thread
should_reload_event = threading.Event()


def jinja_template_directories() -> Set[Path]:
    cwd = Path.cwd()
    items = set()
    for backend in engines.all():
        if not _is_jinja_backend(backend):
            continue

        from jinja2 import FileSystemLoader

        loader = backend.env.loader
        if not isinstance(loader, FileSystemLoader):  # pragma: no cover
            continue

        items.update([cwd / Path(fspath) for fspath in loader.searchpath])
    return items


def _is_jinja_backend(backend: BaseEngine) -> bool:
    """
    Cautious check for Jinja backend, avoiding import which relies on jinja2
    """
    return any(
        f"{c.__module__}.{c.__qualname__}" == "django.template.backends.jinja2.Jinja2"
        for c in backend.__class__.__mro__
    )


# Signal receivers imported in AppConfig.ready() to ensure connected
@receiver(autoreload_started, dispatch_uid="browser_reload")
def on_autoreload_started(*, sender: BaseReloader, **kwargs: Any) -> None:
    for directory in jinja_template_directories():
        sender.watch_dir(directory, "**/*")

    for finder in get_finders():
        if not isinstance(
            finder, (AppDirectoriesFinder, FileSystemFinder)
        ):  # pragma: no cover
            continue
        for storage in finder.storages.values():
            sender.watch_dir(Path(storage.location), "**/*")


@receiver(file_changed, dispatch_uid="browser_reload")
def on_file_changed(*, file_path: Path, **kwargs: Any) -> Optional[bool]:
    # Django Templates
    if HAVE_DJANGO_TEMPLATE_DIRECTORIES:
        for template_dir in django_template_directories():
            if template_dir in file_path.parents:
                should_reload_event.set()
                return None

    # Jinja Templates
    for template_dir in jinja_template_directories():
        if template_dir in file_path.parents:
            should_reload_event.set()
            return True

    return None


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
