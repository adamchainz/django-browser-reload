====================
django-launch-editor
====================

.. image:: https://img.shields.io/github/actions/workflow/status/adamchainz/django-launch-editor/main.yml.svg?branch=main&style=for-the-badge
   :target: https://github.com/adamchainz/django-launch-editor/actions?workflow=CI

.. image:: https://img.shields.io/badge/Coverage-100%25-success?style=for-the-badge
   :target: https://github.com/adamchainz/django-launch-editor/actions?workflow=CI

.. image:: https://img.shields.io/pypi/v/django-launch-editor.svg?style=for-the-badge
   :target: https://pypi.org/project/django-launch-editor/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

----

Open files from Django’s debug error page in your editor.

Adds “Open in editor” buttons to the traceback on Django’s debug error page, which open the file at the right line in your editor, using `launch-editor-py <https://github.com/adamchainz/launch-editor-py>`__.

----

**Improve your Django and Git skills** with `my books <https://adamj.eu/books/>`__.

----

Requirements
------------

Python 3.11 to 3.15 supported.

Django 5.2 to 6.1 supported.

Installation
------------

1. Install with **pip**:

   .. code-block:: sh

       python -m pip install django-launch-editor

2. Set Django’s exception reporter class, in your settings file:

   .. code-block:: python

       DEFAULT_EXCEPTION_REPORTER = (
           "django_launch_editor.reporter.LaunchEditorExceptionReporter"
       )

   If you already use a custom exception reporter, make it subclass ``LaunchEditorExceptionReporter`` instead.

3. Include the app URLs in your root URLconf:

   .. code-block:: python

       from django.urls import include, path

       urlpatterns = [
           ...,
           path("__launch_editor__/", include("django_launch_editor.urls")),
       ]

   You can use another prefix if required.

That’s it! 🎉
Trigger an error with ``DEBUG = True``, and each traceback frame, plus any template error, will have an “Open in editor” button.

Editor selection
----------------

launch-editor-py picks your editor from, in order:

1. The ``LAUNCH_EDITOR`` environment variable.
2. A supported editor that is currently running.
3. The ``VISUAL`` environment variable.
4. The ``EDITOR`` environment variable.

Set ``LAUNCH_EDITOR`` in the environment of your development server if the wrong editor opens, for example ``LAUNCH_EDITOR=code``.
See `the launch-editor-py documentation <https://github.com/adamchainz/launch-editor-py#guess_editoreditornone>`__ for more details and the list of supported editors.

The editor runs on the machine running Django, so this package is only useful when you develop locally.

Security
--------

Opening files runs a program on the server, so the package takes several precautions:

* Buttons are only added, and the view only works, when ``DEBUG`` is ``True``.
  Otherwise, the view returns a 404.
  Buttons are never added to error emails.

* The view only accepts ``POST`` requests, with CSRF protection, even if ``CsrfViewMiddleware`` is not installed.

* The view doesn’t accept arbitrary file paths.
  Instead, each button carries a token, signed with your ``SECRET_KEY``, for a file and line that appeared on a debug page.
  Tokens are only made for files that exist, and expire after 24 hours.

How it works
------------

``LaunchEditorExceptionReporter`` extends Django’s ``ExceptionReporter`` to add a small script to the HTML debug page, along with signed tokens for each traceback frame.
The script adds buttons that ``POST`` a token to the view, which checks it and calls ``launch_editor()``.
