Example Project
===============

Use Python 3.11 to set up and run with these commands:

.. code-block:: sh

   python -m venv venv
   source venv/bin/activate
   python -m pip install -U pip wheel
   python -m pip install -r requirements.txt -e ..
   DEBUG=1 python manage.py runserver

Open it at http://127.0.0.1:8000/ .

Open your browser’s development tools console to see log messages from django-browser-reload.
Then try editing a file to see the browser to automagically reload!

Try editing these files to test the different types of change detection:

* ``example/views.py`` - server restart detection.
* ``templates/django/index.html`` - Django template change detection.
* ``templates/jinja/index.html`` - Jinja template change detection (when on the ``/jinja/`` page).
* ``static/main.css`` - static asset change detection.
