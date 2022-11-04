from __future__ import annotations

from typing import Any

from django.templatetags.static import static
from django_browser_reload.jinja import django_browser_reload_script
from jinja2 import Environment


def environment(**options: Any) -> Environment:
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "django_browser_reload_script": django_browser_reload_script,
        }
    )
    return env
