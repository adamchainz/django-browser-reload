=========
Changelog
=========

1.16.0 (2024-10-11)
-------------------

* Drop Python 3.8 support.

* Support Python 3.13.

1.15.0 (2024-08-15)
-------------------

*Accidental empty release.*

1.14.0 (2024-08-15)
-------------------

* Mark the view as public with ``@login_not_required`` on Django 5.1, for compatibility with ``LoginRequiredMiddleware``.

  Thanks to Macktireh Abdi Soubaneh for the report in `Issue #281 <https://github.com/adamchainz/django-browser-reload/issues/281>`__.

1.13.0 (2024-06-19)
-------------------

* Support Django 5.1.

1.12.1 (2023-11-16)
-------------------

* Fix ASGI compatibility on Python 3.12.

1.12.0 (2023-10-11)
-------------------

* Support Django 5.0.

1.11.0 (2023-07-10)
-------------------

* Drop Python 3.7 support.

1.10.0 (2023-06-14)
-------------------

* Support Python 3.12.

1.9.0 (2023-06-05)
------------------

* Support ASGI on Django 4.2+.

  Thanks to Alexandre Spaeth in `PR #148 <https://github.com/adamchainz/django-browser-reload/pull/148>`__.

1.8.0 (2023-04-11)
------------------

* Support use with `GzipMiddleware`, or other middleware that encodes the response.

1.7.0 (2023-02-25)
------------------

* Support Django 4.2.

1.6.0 (2022-06-05)
------------------

* Support Python 3.11.

* Support Django 4.1.

1.5.0 (2022-05-18)
------------------

* Add async support to the middleware, to reduce overhead on async projects.

* Disable middleware at Django startup when ``DEBUG`` is ``False``.

1.4.0 (2022-05-10)
------------------

* Drop support for Django 2.2, 3.0, and 3.1.

1.3.0 (2022-01-13)
------------------

* “Debounce” reload events with a 50 millisecond window.
  This fixes an issue with repeat triggers of the same reload event.
  It should also help workflows where several files change in quick succession.

1.2.0 (2022-01-10)
------------------

* Drop Python 3.6 support.

1.1.1 (2022-01-10)
------------------

* Prevent restarting the server when static assets change.

  Thanks to Tim Kamanin for the report in `Issue #46 <https://github.com/adamchainz/django-browser-reload/issues/46>`__.

* Use 'defer' in the ``<script>`` tag to avoid blocking HTML parsing.

1.1.0 (2021-12-20)
------------------

* Provide a middleware to insert the script tag.
  This is now the recommended method for doing the insertion, as it automatically applies to all HTML responses.
  This includes Django’s debug page, so you can automatically reload after fixing an exception.

  You can replace use of the script tag with the middleware, unless you need precise control over which pages reloading runs on.

* Reload when static assets or Jinja templates change.

* Mention django-browser-reload in reload debug message.

* Add Jinja template tag.

1.0.0 (2021-12-15)
------------------

* Initial release.
