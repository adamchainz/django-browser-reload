from __future__ import annotations

import asyncio
import json
import threading
from http import HTTPStatus
from pathlib import Path
from typing import Any
from typing import AsyncGenerator
from typing import Callable
from typing import Generator

import django
from django.conf import settings
from django.contrib.staticfiles.finders import AppDirectoriesFinder
from django.contrib.staticfiles.finders import FileSystemFinder
from django.contrib.staticfiles.finders import get_finders
from django.core.files.storage import FileSystemStorage
from django.core.handlers.asgi import ASGIRequest
from django.dispatch import receiver
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http.response import HttpResponseBase
from django.template import engines
from django.template.autoreload import (
    get_template_directories as django_template_directories,
)
from django.template.backends.base import BaseEngine
from django.utils.autoreload import autoreload_started
from django.utils.autoreload import BaseReloader
from django.utils.autoreload import file_changed
from django.utils.crypto import get_random_string

# For detecting when Python has reloaded, use a random version ID in memory.
# When the worker receives a different version from the one it saw previously,
# it reloads.
version_id = get_random_string(32)

# Communicate template changes to the running polls thread
should_reload_event = threading.Event()

reload_timer: threading.Timer | None = None

RELOAD_DEBOUNCE_TIME = 0.05  # seconds


def trigger_reload_soon() -> None:
    global reload_timer
    if reload_timer is not None:
        reload_timer.cancel()

    reload_timer = threading.Timer(RELOAD_DEBOUNCE_TIME, should_reload_event.set)
    reload_timer.start()


def jinja_template_directories() -> set[Path]:
    cwd = Path.cwd()
    items = set()
    for backend in engines.all():
        if not _is_jinja_backend(backend):
            continue

        from jinja2 import FileSystemLoader

        loader = backend.env.loader  # type: ignore [attr-defined]
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


def static_finder_storages() -> Generator[FileSystemStorage, None, None]:
    for finder in get_finders():
        if not isinstance(
            finder, (AppDirectoriesFinder, FileSystemFinder)
        ):  # pragma: no cover
            continue
        yield from finder.storages.values()


# Signal receivers imported in AppConfig.ready() to ensure connected
@receiver(autoreload_started, dispatch_uid="browser_reload")
def on_autoreload_started(*, sender: BaseReloader, **kwargs: Any) -> None:
    for directory in jinja_template_directories():
        sender.watch_dir(directory, "**/*")

    for storage in static_finder_storages():
        sender.watch_dir(Path(storage.location), "**/*")


@receiver(file_changed, dispatch_uid="browser_reload")
def on_file_changed(*, file_path: Path, **kwargs: Any) -> bool | None:
    # Returning True tells Django *not* to reload

    file_parents = file_path.parents

    # Django Templates
    for template_dir in django_template_directories():
        if template_dir in file_parents:
            trigger_reload_soon()
            return True

    # Jinja Templates
    for template_dir in jinja_template_directories():
        if template_dir in file_parents:
            trigger_reload_soon()
            return True

    # Static assets
    for storage in static_finder_storages():
        if Path(storage.location) in file_parents:
            trigger_reload_soon()
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

    if not request.accepts("text/event-stream"):
        return HttpResponse(status=HTTPStatus.NOT_ACCEPTABLE)

    event_stream: Callable[[], AsyncGenerator[bytes, None]] | Callable[
        [], Generator[bytes, None, None]
    ]

    if isinstance(request, ASGIRequest):
        if django.VERSION < (4, 2):
            return HttpResponse(
                "ASGI requires Django 4.2+",
                status=HTTPStatus.NOT_IMPLEMENTED,
                content_type="text/plain",
            )

        async def event_stream() -> AsyncGenerator[bytes, None]:
            while True:
                await asyncio.sleep(PING_DELAY)
                yield message("ping", versionId=version_id)

                if should_reload_event.is_set():
                    should_reload_event.clear()
                    yield message("reload")

    else:

        def event_stream() -> Generator[bytes, None, None]:
            while True:
                yield message("ping", versionId=version_id)

                should_reload = should_reload_event.wait(timeout=PING_DELAY)
                if should_reload:
                    should_reload_event.clear()
                    yield message("reload")

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    # Set a content-encoding to bypass GzipMiddleware etc.
    response["content-encoding"] = ""
    return response
