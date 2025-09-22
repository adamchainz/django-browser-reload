=====================
django-browser-reload
=====================

.. image:: https://img.shields.io/github/actions/workflow/status/adamchainz/django-browser-reload/main.yml.svg?branch=main&style=for-the-badge
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

Automatically refresh your browser on changes to Python code, templates, or static files.

----

**Work smarter and faster** with my book `Boost Your Django DX <https://adamchainz.gumroad.com/l/byddx>`__ which covers django-browser-reload and many other tools.
I wrote django-browser-reload whilst working on the book!

----

Requirements
------------

Python 3.9 to 3.14 supported.

Django 4.2 to 6.0 supported.

Both WSGI and ASGI are supported.

Your browser needs to support:

* |EventSource|__ - universally available.

  .. |EventSource| replace:: ``EventSource``
  __ https://developer.mozilla.org/en-US/docs/Web/API/EventSource#browser_compatibility

* |SharedWorker|__ - available on Chrome, Edge, Firefox, and Opera for a long time.
  Available on Safari since version 16 (2022-09-12).

  .. |SharedWorker| replace:: ``SharedWorker``
  __ https://developer.mozilla.org/en-US/docs/Web/API/SharedWorker#browser_compatibility

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

4. Include the app URLs in your root URLconf:

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

   The middleware should be listed after any others that encode the response, such as Django’s ``GZipMiddleware``.

   The middleware automatically inserts the required script tag on HTML responses before ``</body>`` when ``DEBUG`` is ``True``.
   It does so to every HTML response, meaning it will be included on Django’s debug pages, admin pages, etc.
   If you want more control, you can instead insert the script tag in your templates—see below.

All done! 📯

Try installing `django-watchfiles <https://github.com/adamchainz/django-watchfiles>`__ as well, for faster and more efficient reloading.

Usage
-----

Once set up as above, just run ``runserver`` with the ``DEBUG`` setting set to ``True``, and open your site in a browser.
When you modify Python code, templates, or static assets, the page will automatically reload.
Welcome to much faster iteration times!

If you open multiple tabs, only the most recently used tab will reload.

django-browser works by adding a script tag into HTML responses, just before ``</body>``.
This script connects back to the development server and receives events that tell it when to reload.
These events are triggered through server restarts and ``runserver``\’s autoreload system.
See below for a more detailed explanation, under “How It Works”.

On Django 6.0+ with ``ContentSecurityPolicyMiddleware``, the ``<script>`` tag will include `the Content Security Policy (CSP) nonce <https://docs.djangoproject.com/en/6.0/howto/csp/#nonce-config>`__.

Template tag
------------

You can also use a template tag to insert the script on relevant pages, instead of using the middleware.
This may be useful if you want to restrict reloading to certain pages, or if the middleware doesn’t work for your page structure.
The template tag has both Django templates and Jinja versions, and only outputs the script tag when ``DEBUG`` is ``True``.

For **Django Templates**, load the tag and use it in your base template.
The tag can go anywhere, but it’s best just before ``</body>``:

.. code-block:: html

   {% load django_browser_reload %}

   ...

       {% django_browser_reload_script %}
     </body>
   </html>

On Django 6.0+, the ``<script>`` tag will include `the Content Security Policy (CSP) nonce <https://docs.djangoproject.com/en/6.0/howto/csp/#nonce-config>`__, if it’s present in the context.

To add the template tag within Django’s admin, do so in a template called ``admin/base_site.html``, per Django’s documentation on `extending an overridden template <https://docs.djangoproject.com/en/4.0/howto/overriding-templates/#extending-an-overridden-template>`__.
The template should look like:

.. code-block:: html

    {% extends "admin/base_site.html" %}

    {% load django_browser_reload %}

    {% block extrahead %}
        {{ block.super }}
        {% django_browser_reload_script %}
    {% endblock %}

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

To use a CSP nonce, pass it to the function as ``nonce``:

.. code-block:: jinja

    {{ django_browser_reload_script(nonce=csp_nonce) }}

Example project
---------------

To demonstrate and test django-browser-reload on all kinds of assets, there is an example project included in the repository.
Open |the example directory|__, follow the instructions in its README, and try it out.

.. |the example directory| replace:: the ``example/`` directory
__ https://github.com/adamchainz/django-browser-reload/tree/main/example

How it works
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

The middleware (or template tag) includes a listener script on each page.
This listener script starts or connects to a |SharedWorker2|__, running a worker script.
The worker script then connects to the events view in Django, using an |EventSource2|__ to receive server-sent events.

.. |SharedWorker2| replace:: ``SharedWorker``
__ https://developer.mozilla.org/en-US/docs/Web/API/SharedWorker

.. |EventSource2| replace:: ``EventSource``
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
