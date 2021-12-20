=======
History
=======

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
