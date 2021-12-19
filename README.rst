=====================
django-browser-reload
=====================

.. image:: https://img.shields.io/github/workflow/status/adamchainz/django-browser-reload/CI/main?style=for-the-badge
   :target: https://github.com/adamchainz/django-browser-reload/actions?workflow=CI

.. image:: https://img.shields.io/badge/Coverage-100%25-success?style=for-the-badge
  :target: https://github.com/adamchainz/django-browser-reload/actions?workflow=CI

.. image:: https://img.shields.io/pypi/v/django-browser-reload.svg?style=for-the-badge
   :target: https://pypi.org/project/django-browser-reload/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Automatically reload your browser in development.

Requirements
------------

Python 3.6 to 3.10 supported.

Django 2.2 to 4.0 supported.

----

**Are your tests slow?**
Check out my book `Speed Up Your Django Tests <https://gumroad.com/l/suydt>`__ which covers loads of best practices so you can write faster, more accurate tests.

----

Installation
------------

1. Install with **pip**:

   .. code-block:: sh

       python -m pip install django-browser-reload

2. Ensure you have ``"django.contrib.staticfiles"`` in your ``INSTALLED_APPS``.

3. Add django-browser-reload to your ``INSTALLED_APPS``:

   .. code-block:: python

       INSTALLED_APPS = [
           ...,
           "django_browser_reload",
           ...,
       ]

4. Include the app URL’s in your root URLconf(s):

   .. code-block:: python

       from django.urls import include, path

       urlpatterns = [
           ...,
           path("__reload__/", include("django_browser_reload.urls")),
       ]

   You can use another prefix if required.

5. Add the middleware:

   .. code-block:: python

      MIDDLEWARE = [
          # ...
          "django_browser_reload.middleware.BrowserReloadMiddleware",
          # ...
      ]

   The middleware should be listed after any that encode the response, such as Django’s ``GZipMiddleware``.

   The middleware automatically inserts the required script tag on HTML responses when ``DEBUG`` is ``True``.
   It does so to every HTML response, meaning it will be included on Django’s debug pages, admin pages, etc.
   If you want more control, you can instead insert the script tag in your templates—see below.

All done! 📯

For faster and more efficient reloading, also set up `Django’s built-in Watchman support <https://adamj.eu/tech/2021/01/20/efficient-reloading-in-djangos-runserver-with-watchman/>`__.

What It Does
------------

When ``DEBUG`` is ``True``, the template tag includes a small script.
This script connects back to the development server and will automatically reload when static assets or templates are modified, or after ``runserver`` restarts.
(Detecting modification of Django templates requires Django 3.2+.)
The reload only happens in the most recently opened tab.

Example App
-----------

See the `example app <https://github.com/adamchainz/django-browser-reload/tree/main/example>`__ in the ``example/`` directory of the GitHub repository.
Start it up, and try modifying ``example/core/views.py`` or ``templates/*/index.html`` to see the reloading in action.

Template Tag
------------

If the middleware doesn’t work for you, you can also use a template tag to insert the script on relevant pages.
The template tag has both Django templates and Jinja versions, and only outputs the script tag when ``DEBUG`` is ``True``.

For **Django Templates**, load the tag and use it in your base template.
The tag can go anywhere, but it’s best just before ``</body>``:

.. code-block:: html

   {% load django_browser_reload %}

   ...

       {% django_browser_reload_script %}
     </body>
   </html>

To add django-browser-reload to Django’s admin, do so in a template called ``admin/base_site.html``:

.. code-block:: html

    {% extends "admin/base_site.html" %}

    {% load django_browser_reload %}

    {% block extrahead %}
        {{ block.super }}
        {% django_browser_reload_script %}
    {% endblock %}

This follows Django’s documentation on `extending an overriden template <https://docs.djangoproject.com/en/4.0/howto/overriding-templates/#extending-an-overridden-template>`__.

For **Jinja Templates**, you need to perform two steps.
First, load the tag function into the globals of your `custom environment <https://docs.djangoproject.com/en/stable/topics/templates/#django.template.backends.jinja2.Jinja2>`__:

.. code-block:: python

    # myproject/jinja2.py
    from jinja2 import Environment
    from django_browser_reload.jinja import django_browser_reload_script


    def environment(**options):
        env = Environment(**options)
        env.globals.update(
            {
                # ...
                "django_browser_reload_script": django_browser_reload_script,
            }
        )
        return env

Second, render the tag in your base template.
It can go anywhere, but it’s best just before ``</body>``:

.. code-block:: html

    ...
        {{ django_browser_reload_script() }}
      </body>
    </html>

Ta-da!

How It Works
------------

Here’s a diagram:

.. code-block:: text

                                         Browser

                                 Tab 1    Tab 2     Tab N
                               listener  listener  listener
                                    \       |       /
      Django                         \      |      /
                                      \     |     /
    Events View --------------------> Shared worker

The template tag includes a listener script on each page.
This listener script starts or connects to a |SharedWorker|__, running a worker script.
The worker script then connects to the events view in Django, using an |EventSource|__ to receive server-sent events.

.. |SharedWorker| replace:: ``SharedWorker``
__ https://developer.mozilla.org/en-US/docs/Web/API/SharedWorker

.. |EventSource| replace:: ``EventSource``
__ https://developer.mozilla.org/en-US/docs/Web/API/EventSource

This event source uses |StreamingHttpResponse|__ to send events to the worker.
The view continues streaming events indefinitely, until disconnected.
(This requires a thread and will not work if you use ``runserver``\’s |--nothreading option|__.)

.. |--nothreading option| replace:: ``--nothreading`` option
__ https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-runserver-nothreading

On a relevant event, the worker will reload the most recently connected tab.
(It avoids reloading *all* tabs since that could be expensive.)

.. |StreamingHttpResponse| replace:: ``StreamingHttpResponse``
__ https://docs.djangoproject.com/en/stable/ref/request-response/#django.http.StreamingHttpResponse

To reload when a template changes, django-browser-reload piggybacks on Django’s autoreloading infrastructure.
An internal Django signal indicates when a template file has changed.
The events view receives this signal and sends an event to the worker, which triggers a reload.
There is no smart filtering - if *any* template file changes, the view is reloaded.

To reload when the server restarts, django-browser-reload uses a version ID.
This ID is randomly generated when the view module is imported, so it will be different every time the server starts.
When the server restarts, the worker’s ``EventSource`` reconnects with minimal delay.
On connection, the events view sends the version ID, which the worker sees as different, so it triggers a reload.

The events view also sends the version ID every second to keep the connection alive.

Compatibility
-------------

``EventSource`` is `highly compatible <https://developer.mozilla.org/en-US/docs/Web/API/EventSource#browser_compatibility>`__.
``SharedWorker`` is `a bit less so <https://developer.mozilla.org/en-US/docs/Web/API/SharedWorker#browser_compatibility>`__, but should work with Chrome, Edge, Firefox, and Opera.
