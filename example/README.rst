Example Project
===============

Run the server with:

.. code-block:: sh

   uv run manage.py runserver

Open it at http://127.0.0.1:8000/ to see the debug error page for a ``KeyError``.
Click a file location, like “…/views.py, line 20”, to open it in your editor.

If the wrong editor opens, set the ``LAUNCH_EDITOR`` environment variable, for example:

.. code-block:: sh

   LAUNCH_EDITOR=code uv run manage.py runserver
