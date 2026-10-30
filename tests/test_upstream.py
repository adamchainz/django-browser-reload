from __future__ import annotations

import difflib
import inspect
from textwrap import dedent

from django.test import SimpleTestCase
from django.views.debug import ExceptionReporter

from django_launch_editor.reporter import LaunchEditorExceptionReporter


class UpstreamTests(SimpleTestCase):
    """
    Check code copied from Django against the original, so upstream changes
    are noticed. If a test fails, integrate the change, then update the
    expected diff. See:
    https://adamj.eu/tech/2024/04/26/python-diffing-unit-test/
    """

    def test_get_traceback_html(self):
        upstream = inspect.getsource(ExceptionReporter.get_traceback_html)
        ours = inspect.getsource(LaunchEditorExceptionReporter.get_traceback_html)

        diff = "".join(
            difflib.unified_diff(
                upstream.splitlines(keepends=True),
                ours.splitlines(keepends=True),
                fromfile="upstream",
                tofile="ours",
            )
        )

        assert diff == dedent(
            '''\
            --- upstream
            +++ ours
            @@ -1,6 +1,14 @@
            -    def get_traceback_html(self):
            +    def get_traceback_html(self) -> SafeString:
                     """Return HTML version of debug 500 HTTP error page."""
            +        data = self.get_traceback_data()
                     with self.html_template_path.open(encoding="utf-8") as fh:
                         t = DEBUG_ENGINE.from_string(fh.read())
            -        c = Context(self.get_traceback_data(), use_l10n=False)
            -        return t.render(c)
            +        c = Context(data, use_l10n=False)
            +        html = t.render(c)
            +
            +        extra = self.get_launch_editor_html(data)
            +        if extra:
            +            before, body_end, after = html.rpartition("</body>")
            +            if body_end:
            +                html = mark_safe(before + extra + body_end + after)
            +        return html
            '''
        )
