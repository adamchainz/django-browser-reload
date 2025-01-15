from __future__ import annotations

from django.core.checks import Error


def check_django_browser_reload_setup(**kwargs):
    """
    Check if the necessary settings for django-browser-reload are correctly configured.
    """
    from django.conf import settings

    errors = []

    if "django.contrib.staticfiles" not in settings.INSTALLED_APPS:
        errors.append(
            Error(
                "The 'staticfiles' app must be installed.",
                id="django_browser_reload.E001",
            )
        )
    if (
        "django_browser_reload.middleware.BrowserReloadMiddleware"
        not in settings.MIDDLEWARE
    ):
        errors.append(
            Error(
                "The 'BrowserReloadMiddleware' must be added to MIDDLEWARE.",
                id="django_browser_reload.E002",
            )
        )
    if "django.contrib.staticfiles.finders.AppDirectoriesFinder" not in getattr(
        settings, "STATICFILES_FINDERS", []
    ):
        errors.append(
            Error(
                "'AppDirectoriesFinder' must be added to STATICFILES_FINDERS.",
                id="django_browser_reload.E003",
            )
        )
    return errors
