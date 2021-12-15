from pathlib import Path
from typing import Any, Dict, List

ALLOWED_HOSTS: List[str] = []

BASE_DIR = Path(__file__).resolve().parent

DATABASES: Dict[str, Dict[str, Any]] = {}

INSTALLED_APPS = [
    # Third Party
    "django_browser_reload",
    # Contrib
    "django.contrib.staticfiles",
]

MIDDLEWARE: List[str] = []

ROOT_URLCONF = "tests.urls"

SECRET_KEY = "NOTASECRET"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {"context_processors": []},
    }
]

USE_TZ = True

# 2. Django Contrib Settings

# django.contrib.staticfiles

STATIC_URL = "static/"
