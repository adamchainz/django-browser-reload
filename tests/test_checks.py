from __future__ import annotations

from django.core.checks import run_checks
from django.test import SimpleTestCase
from django.test.utils import override_settings


class TestDjangoBrowserReloadChecks(SimpleTestCase):
    @override_settings(INSTALLED_APPS=[])
    def test_staticfiles_not_installed(self):
        errors = run_checks()
        assert any(error.id == "django_browser_reload.E001" for error in errors)

    @override_settings(MIDDLEWARE=[])
    def test_middleware_not_installed(self):
        errors = run_checks()
        assert any(error.id == "django_browser_reload.E002" for error in errors)

    @override_settings(STATICFILES_FINDERS=[])
    def test_app_directories_finder_not_installed(self):
        errors = run_checks()
        assert any(error.id == "django_browser_reload.E003" for error in errors)

    @override_settings(
        INSTALLED_APPS=["django.contrib.staticfiles"],
        MIDDLEWARE=["django_browser_reload.middleware.BrowserReloadMiddleware"],
        STATICFILES_FINDERS=["django.contrib.staticfiles.finders.AppDirectoriesFinder"],
    )
    def test_all_correctly_installed(self):
        errors = run_checks()
        assert errors == []
