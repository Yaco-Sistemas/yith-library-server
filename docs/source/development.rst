Development
===========

Running the tests
-----------------

Running Yith Library Server unit tests is as easy as it could be:

.. code-block:: bash

   python setup.py test


Generating the documentation
----------------------------

Yith Library Server uses Sphinx for its documentation. The document files
are inside the `docs` directory. If you want to generate them from the
sources you can use the included Makefile:

.. code-block:: bash

   cd docs
   make html

And the result will be copied into the `docs/build/html` directory where you
can point your favourite browser and enjoy the reading.

There are many more different output formats available for the documentation.
Try typing `make help` to get a glimpse at them.

.. note::

   For more information about Sphinx and their output formats, read its
   documentation at http://sphinx.pocoo.org/
