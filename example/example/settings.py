from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Hide development server warning
# https://docs.djangoproject.com/en/stable/ref/django-admin/#envvar-DJANGO_RUNSERVER_HIDE_WARNING
os.environ["DJANGO_RUNSERVER_HIDE_WARNING"] = "true"

asgi = os.environ.get("ASGI") == "1"

# 1. Django Core Settings

# Dangerous: disable host header validation
ALLOWED_HOSTS = ["*"]

BASE_DIR = Path(__file__).resolve().parent

DATABASES: dict[str, dict[str, Any]] = {}

DEBUG = True

INSTALLED_APPS = [
    # Project
    "example",
    # Third Party
    "django_browser_reload",
    # Contrib
    "django.contrib.staticfiles",
]
if asgi:
    INSTALLED_APPS.insert(1, "daphne")

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "example.urls"

SECRET_KEY = "django-insecure-WCglZv2CA4v59K24bXfADwNDXc3HlwDY"  # typos: ignore

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates" / "django"],
        "APP_DIRS": True,
    },
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates" / "jinja"],
        "OPTIONS": {
            "environment": "example.jinja.environment",
        },
    },
]

USE_TZ = True

# 2. Django Contrib Settings

# django.contrib.staticfiles

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = "/static/"

# 3. Third party apps

# daphne

ASGI_APPLICATION = "example.asgi.app"
