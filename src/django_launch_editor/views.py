from __future__ import annotations

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.core.signing import BadSignature
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from launch_editor import LaunchEditorError, launch_editor

from django_launch_editor.tokens import load_token


@login_not_required
def launch(request: HttpRequest) -> HttpResponse:
    # Check DEBUG first, so nothing else about the view is revealed when it’s
    # off.
    if not settings.DEBUG:
        raise Http404()
    return _launch(request)


# Apply CSRF protection even if CsrfViewMiddleware is not installed.
@csrf_protect
@require_POST
def _launch(request: HttpRequest) -> HttpResponse:
    # Only files and lines that were signed when rendering a debug page can
    # be opened, rather than any file the client asks for.
    try:
        filename, line = load_token(request.POST.get("token", ""))
    except BadSignature:
        return JsonResponse(
            {"error": "Invalid or expired token. Reload the page and try again."},
            status=HTTPStatus.BAD_REQUEST,
        )

    try:
        launch_editor(filename, line)
    except LaunchEditorError as exc:
        return JsonResponse(
            {"error": str(exc)},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    return HttpResponse(status=HTTPStatus.NO_CONTENT)
