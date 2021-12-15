from typing import Any, Dict, List

SECRET_KEY = "NOTASECRET"

ALLOWED_HOSTS: List[str] = []

DATABASES: Dict[str, Dict[str, Any]] = {}

INSTALLED_APPS = [
    # Third Party
    "django_browser_reload",
    # Contrib
    "django.contrib.staticfiles",
]

MIDDLEWARE: List[str] = []

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {"context_processors": []},
    }
]

USE_TZ = True

# 2. Django Contrib Settings

# django.contrib.staticfiles

STATIC_URL = "static/"
