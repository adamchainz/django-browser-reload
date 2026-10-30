from __future__ import annotations

from pathlib import Path
from typing import Any

ALLOWED_HOSTS: list[str] = []

BASE_DIR = Path(__file__).resolve().parent

DATABASES: dict[str, dict[str, Any]] = {}

DEFAULT_EXCEPTION_REPORTER = (
    "django_launch_editor.reporter.LaunchEditorExceptionReporter"
)

INSTALLED_APPS: list[str] = []

MIDDLEWARE = [
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "tests.urls"

SECRET_KEY = "NOTASECRET"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {"context_processors": []},
    },
]

USE_TZ = True
