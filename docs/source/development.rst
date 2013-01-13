.. _development_chapter:

Developing :program:`Yith Library Server`
=========================================

Installing in development mode
------------------------------

Installing :program:`Yith Library Server` in development mode is
very similar to the regular installation describe in the
:ref:`installation_chapter` section. The only difference is about the
installation of :program:`Yith Library Server` in the Virtual
Python Environment.

In the *regular installation* you perform these commands:

.. code-block:: text

   $ cd env
   $ bin/easy_install yith-library-server

In *development mode* you execute these commands instead:

.. code-block:: text

   $ cd env
   $ git clone git://github.com/Yaco-Sistemas/yith-library-server.git
   $ cd yith-library-server
   $ ../bin/python setup.py develop

In order to perform development tasks like running the tests or
building the documentation it is recommended to activate the
Virtual Python Environment. This way the Python interpreter used
will always be taken from the Virtual Python Environment.

To activate the Virtual Python Environment, execute this command:

.. code-block:: text

   $ cd env
   $ source bin/activate
   $ cd yith-library-server

Running the tests
-----------------

In order to run the tests you should install extra packages such
as ``nose`` and ``coverage``. Fortunately this is easily achieved
with this command:

.. code-block:: text

   (env)$ python setup.py testing

Now running :program:`Yith Library Server` tests is as easy as it
could be:

.. code-block:: text

   (env)$ python setup.py test

You can also get the current test coverage with this command:

.. code-block:: text

   (env)$ python setup.py nosetests

Generating the documentation
----------------------------

:program:`Yith Library Server` uses `Sphinx <http://sphinx-doc.org/>`_
for its documentation. The document files are inside the `docs` directory.

If you want to generate them from the sources you need to install
the required packages:

.. code-block:: text

   (env)$ python setup.py docs

Now you can generate the documentation using the provided Makefile

.. code-block:: text

   (env)$ cd docs
   (env)$ make html

And the result will be copied into the `docs/build/html` directory where you
can point your favourite browser and enjoy the reading.

There are many more different output formats available for the documentation.
Try typing `make help` to get a glimpse at them.

.. note::

   For more information about Sphinx and their output formats, read its
   documentation at http://sphinx.pocoo.org/
