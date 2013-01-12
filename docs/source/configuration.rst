.. _configuration_chapter:

Configuring :program:`Yith Library Server`
==========================================

How the configuration is read
-----------------------------

:program:`Yith Library Server` read its configuration options from
two different sources:

- A configuration file with a INI syntax
- Environment variables. This work for many options but not all of them.

If an option is defined both in the configuration file and an
environment variable, :program:`Yith Library Server` will use the
value of the environment variable.

:program:`Yith Library Server` comes with two configuration
templates, one for development and one for production purposes.
You should copy one of these templates instead of editing them
because that would make the upgrade process easier.

The development template is named :file:`development.ini` and the
production template is named :file:`production.ini`. These templates
have plenty of comments so it should not be very hard to get
started with them.

Once you have your configuration options established in a
configuration file you can run :program:`Yith Library Server`
using the following command:

.. code-block:: text

   pserve configuration_file.ini
     Starting server in PID 6743.
     serving on http://0.0.0.0:6543


Configuration options
---------------------

Authentication
~~~~~~~~~~~~~~

Available languages
~~~~~~~~~~~~~~~~~~~

This option defines the set of available languages that
:program:`Yith Library Server` will use for internationalization
purposes. The value is a space delimited list of iso codes.

.. code-block:: text

   available_languages = en es

The default value for this option is ``en es``, which means
there is support for English and Spanish.

As of this writing only English and Spanish translation of UI
text messages are available. With this configuration option
you can restrict the set of available languages but it you add
new languages to it, their translatation catalogs will not be
generated magically.

This option does not have a environment variable. You can only
set it with a configuration file.

CORS support
~~~~~~~~~~~~

Database
~~~~~~~~

Facebook authentication
~~~~~~~~~~~~~~~~~~~~~~~

Google Analytics support
~~~~~~~~~~~~~~~~~~~~~~~~

Google authentication
~~~~~~~~~~~~~~~~~~~~~

Logging
~~~~~~~

Mail
~~~~

Persona authentication
~~~~~~~~~~~~~~~~~~~~~~

Sessions
~~~~~~~~

Twitter authentication
~~~~~~~~~~~~~~~~~~~~~~
