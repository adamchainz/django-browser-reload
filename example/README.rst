Example Application
===================

Use Python 3.10 to set up and run with these commands:

.. code-block:: sh

   python -m venv venv
   source venv/bin/activate
   python -m pip install -U pip wheel
   python -m pip install -r requirements.txt -e ..
   DEBUG=1 python manage.py runserver

Open it at http://127.0.0.1:8000/ .

Open your browser’s development tools console to see log messages from django-browser-reload.
Edit ``example/core/views.py`` or ``templates/index.html`` to see the browser automagically reload!
