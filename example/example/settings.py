import os
from pathlib import Path
from typing import Any, Dict

# 1. Django Core Settings

# Dangerous: disable host header validation
ALLOWED_HOSTS = ["*"]

BASE_DIR = Path(__file__).resolve().parent

DATABASES: Dict[str, Dict[str, Any]] = {}

DEBUG = os.environ.get("DEBUG", "") == "1"

INSTALLED_APPS = [
    # Project
    "example.core",
    # Third Party
    "django_browser_reload",
    # Contrib
    "django.contrib.staticfiles",
]

ROOT_URLCONF = "example.urls"

SECRET_KEY = "django-insecure-WCglZv2CA4v59K24bXfADwNDXc3HlwDY"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
    }
]

USE_TZ = True

# 2. Django Contrib Settings

# django.contrib.staticfiles

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = "static/"
