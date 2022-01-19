from __future__ import annotations

from pathlib import Path
from typing import Any

ALLOWED_HOSTS: list[str] = []

BASE_DIR = Path(__file__).resolve().parent

DATABASES: dict[str, dict[str, Any]] = {}

INSTALLED_APPS = [
    # Third Party
    "django_browser_reload",
    # Contrib
    "django.contrib.staticfiles",
]

MIDDLEWARE: list[str] = []

ROOT_URLCONF = "tests.urls"

SECRET_KEY = "NOTASECRET"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates" / "django"],
        "OPTIONS": {"context_processors": []},
    },
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates" / "jinja"],
    },
]

USE_TZ = True

# 2. Django Contrib Settings

# django.contrib.staticfiles

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = "/static/"
