from __future__ import annotations

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.core.signing import BadSignature
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from launch_editor import LaunchEditorError, launch_editor

from django_launch_editor.tokens import load_token


# Exempt from CsrfViewMiddleware, since its cookie may not have been set on
# the error page, such as for errors raised in middleware before it. Instead,
# cross-site requests are blocked with is_same_origin().
@csrf_exempt
@login_not_required
def launch(request: HttpRequest) -> HttpResponse:
    # Check DEBUG first, so nothing else about the view is revealed when it’s
    # off.
    if not settings.DEBUG:
        raise Http404()
    return _launch(request)


@require_POST
def _launch(request: HttpRequest) -> HttpResponse:
    if not is_same_origin(request):
        return JsonResponse(
            {"error": "Cross-origin requests are not allowed."},
            status=HTTPStatus.FORBIDDEN,
        )

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


def is_same_origin(request: HttpRequest) -> bool:
    """
    Check the request came from a page on the same origin, using headers that
    browsers set and pages cannot forge. Browsers send Sec-Fetch-Site on all
    requests, and Origin on all POST requests, so require one of them.
    """
    sec_fetch_site = request.headers.get("Sec-Fetch-Site")
    if sec_fetch_site is not None:
        return sec_fetch_site == "same-origin"

    origin = request.headers.get("Origin")
    if origin is not None:
        return origin == f"{request.scheme}://{request.get_host()}"

    return False
