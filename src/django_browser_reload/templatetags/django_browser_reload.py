from __future__ import annotations

from django.template import Context, Library

from django_browser_reload.jinja import (
    django_browser_reload_script as base_django_browser_reload_script,
)

register = Library()


@register.simple_tag(takes_context=True)
def django_browser_reload_script(context: Context) -> str:
    return base_django_browser_reload_script(nonce=context.get("csp_nonce"))
