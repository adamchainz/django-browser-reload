from django import template

from django_browser_reload.jinja import django_browser_reload_script

register = template.Library()
register.simple_tag(django_browser_reload_script)
