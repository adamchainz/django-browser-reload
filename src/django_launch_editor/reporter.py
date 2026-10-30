from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings
from django.template import Context
from django.urls import NoReverseMatch, reverse
from django.utils.html import json_script
from django.utils.safestring import SafeString, mark_safe
from django.views.debug import DEBUG_ENGINE, ExceptionReporter

from django_launch_editor.tokens import make_token

SCRIPT = (Path(__file__).parent / "launch-editor.js").read_text(encoding="utf-8")

STYLE = """
button.django-launch-editor {
  background: none; border: none; padding: 0; margin: 0;
  font: inherit; color: inherit; text-align: inherit;
  text-decoration: underline; cursor: pointer;
}
button.django-launch-editor:hover { text-decoration-thickness: 2px; }
button.django-launch-editor .fname { user-select: text; }
button.django-launch-editor:disabled { cursor: progress; }
.django-launch-editor-status { color: #666; }
.django-launch-editor-status.error { color: #c00; }
"""


class LaunchEditorExceptionReporter(ExceptionReporter):
    """
    Exception reporter that adds “Open in editor” buttons to the debug error
    page.
    """

    # Copied from Django, see tests/test_upstream.py.
    def get_traceback_html(self) -> SafeString:
        """Return HTML version of debug 500 HTTP error page."""
        data = self.get_traceback_data()
        with self.html_template_path.open(encoding="utf-8") as fh:
            t = DEBUG_ENGINE.from_string(fh.read())
        c = Context(data, use_l10n=False)
        html = t.render(c)

        extra = self.get_launch_editor_html(data)
        if extra:
            before, body_end, after = html.rpartition("</body>")
            if body_end:
                html = mark_safe(before + extra + body_end + after)
        return html

    def get_launch_editor_html(self, data: dict[str, Any]) -> str:
        # Never add buttons to error emails, or when DEBUG is off, since the
        # view will not work then.
        if not settings.DEBUG or self.is_email or self.request is None:
            return ""

        try:
            url = reverse("django_launch_editor:launch")
        except NoReverseMatch:
            return ""

        frames = [
            make_token(frame["filename"], frame["lineno"])
            if frame["tb"] is not None
            else None
            for frame in data["frames"]
        ]

        template_info = data["template_info"]
        if template_info:
            template = make_token(template_info["name"], template_info["line"])
        else:
            template = None

        config = {
            "url": url,
            "frames": frames,
            "template": template,
        }
        return (
            f"<style>{STYLE}</style>"
            + json_script(config, "django-launch-editor-data")
            + f"<script>{SCRIPT}</script>"
        )
