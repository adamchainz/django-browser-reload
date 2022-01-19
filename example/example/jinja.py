from __future__ import annotations

from typing import Any

from django.templatetags.static import static
from jinja2 import Environment

from django_browser_reload.jinja import django_browser_reload_script


def environment(**options: Any) -> Environment:
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "django_browser_reload_script": django_browser_reload_script,
        }
    )
    return env
