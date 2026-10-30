from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Hide development server warning
# https://docs.djangoproject.com/en/stable/ref/django-admin/#envvar-DJANGO_RUNSERVER_HIDE_WARNING
os.environ["DJANGO_RUNSERVER_HIDE_WARNING"] = "true"

# 1. Django Core Settings

ALLOWED_HOSTS: list[str] = []

BASE_DIR = Path(__file__).resolve().parent

DATABASES: dict[str, dict[str, Any]] = {}

DEBUG = True

DEFAULT_EXCEPTION_REPORTER = (
    "django_launch_editor.reporter.LaunchEditorExceptionReporter"
)

INSTALLED_APPS: list[str] = []

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "example.urls"

SECRET_KEY = "django-insecure-u4Vb2WZq8sKxN7mLpR3tYh6JcD9fGe1A"  # typos: ignore

USE_TZ = True
