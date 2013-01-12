.. _installation_chapter:

Installing :program:`Yith Library Server`
=========================================

Before you install
------------------

You will need `Python <http://python.org>`_ version 2.6 or better to
run :program:`Yith Library Server`.

.. sidebar:: Python Versions

    As of this writing, :program:`Yith Library Server` has been tested
    under Python 2.6, Python 2.7, Python 3.2, and Python 3.3.
    :program:`Yith Library Server` does not run under any version
    of Python before 2.6.

:program:`Yith Library Server` is known to run on all popular UNIX-like
systems such as Linux, MacOS X, and FreeBSD.  It is also known to run on
:term:`PyPy` (1.9+).

:program:`Yith Library Server` installation requires the compilation
of some C code, because of some dependencies (:term:`PyMongo`) so you
will need a Python interpreter that meets the requirements mentioned,
a C compiler and the matching Python development headers for your
interpreter version.

If You Don't Yet Have A Python Interpreter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your system doesn't have a Python interpreter, and you're on UNIX,
you can either install Python using your operating system's package
manager *or* you can install Python from source fairly easily on any
UNIX system that has development tools.

.. index::
   pair: install; Python (from package)

Package Manager Method
++++++++++++++++++++++

You can use your system's "package manager" to install Python. Every
system's package manager is slightly different, but the "flavor" of
them is usually the same.

For example, on an Ubuntu Linux system, to use the system package
manager to install a Python 2.7 interpreter, use the following
command:

.. code-block:: text

   $ sudo apt-get install python2.7-dev

This command will install both the Python interpreter and its development
header files.

The equivalent command in an rpm based Linux system such as Fedora is
this one:

.. code-block:: text

   $ sudo yum install python-devel

Once these steps are performed, the Python interpreter will usually be
invokable via ``python2.7`` from a shell prompt.

.. index::
   pair: install; Python (from source, UNIX)

Source Compile Method
+++++++++++++++++++++

It's useful to use a Python interpreter that *isn't* the "system"
Python interpreter to develop your software.  The authors of
:program:`Yith Library Server` tend not to use the system Python for
development purposes; always a self-compiled one.  Compiling Python
is usually easy, and often the "system" Python is compiled with
options that aren't optimal for web development.

To compile software on your UNIX system, typically you need
development tools.  Often these can be installed via the package
manager. For example, this works to do so on an Ubuntu Linux system:

.. code-block:: text

   $ sudo apt-get install build-essential

On a Fedora Linux system the equivalent command is:

.. code-block:: text

   $ sudo yum groupinstall "Development Tools"

On Mac OS X, installing `XCode
<http://developer.apple.com/tools/xcode/>`_ has much the same effect.

Once you've got development tools installed on your system, you can
install a Python 2.7 interpreter from *source*, on the same system,
using the following commands:

.. code-block:: text

   [lgs@localhost ~]$ cd ~
   [lgs@localhost ~]$ mkdir tmp
   [lgs@localhost ~]$ mkdir opt
   [lgs@localhost ~]$ cd tmp
   [lgs@localhost tmp]$ wget \
          http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz
   [lgs@localhost tmp]$ tar xvzf Python-2.7.3.tgz
   [lgs@localhost tmp]$ cd Python-2.7.3
   [lgs@localhost Python-2.7.3]$ ./configure \
           --prefix=$HOME/opt/Python-2.7.3
   [lgs@localhost Python-2.7.3]$ make; make install

Once these steps are performed, the Python interpreter will be
invokable via ``$HOME/opt/Python-2.7.3/bin/python`` from a shell
prompt.

.. index::
   pair: install; Python (from package, Windows)

Installing :program:`Yith Library Server`
-----------------------------------------

It is best practice to install :command:`Yith Library Server`
into a "virtual" Python environment in order to obtain isolation
from any "system" packages you've got installed in your Python
version.  This can be done by using the :term:`virtualenv` package.
Using a virtualenv will also prevent :command:`Yith Library Server`
from globally installing versions of packages that are not compatible
with your system Python.

To set up a virtualenv in which to install :command:`Yith Library Server`,
first ensure that :term:`setuptools` or :term:`distribute` is installed.
To do so, invoke ``import setuptools`` within the Python interpreter
you'd like to run :command:`Yith Library Server` under.

Here's the output you'll expect if setuptools or distribute is already
installed:

.. code-block:: text

   [lgs@localhost docs]$ python2.7
   Python 2.7.3 (default, Jul 24 2012, 10:05:39)
   [GCC 4.7.0] on linux2
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import setuptools
   >>>

Here's the output you can expect if setuptools or distribute is not already
installed:

.. code-block:: text

   [lgs@localhost docs]$ python2.7
   Python 2.7.3 (default, Jul 24 2012, 10:05:39)
   [GCC 4.7.0] on linux2
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import setuptools
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   ImportError: No module named setuptools
   >>>

If ``import setuptools`` raises an :exc:`ImportError` as it does above, you
will need to install setuptools or distribute manually.

If you are using a "system" Python (one installed by your OS distributor)
you can usually install the setuptools or distribute package by using your
system's package manager. If you cannot do this, or if you're using a
self-installed version of Python, you will need to install setuptools or
distribute "by hand".  Installing setuptools or distribute "by hand" is
always a reasonable thing to do, even if your package manager already has
a pre-chewed version of setuptools for installation.

If you're using Python 2, you'll want to install ``setuptools``.  If you're
using Python 3, you'll want to install ``distribute``.  Below we tell you how
to do both.

Installing Setuptools On Python 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Package Manager Method
++++++++++++++++++++++

If you are using a "system" Python it is recommended that you install
the ``setuptools`` package from your OS distributor. For example, this works
to do so on an Ubuntu Linux system:

.. code-block:: text

   $ sudo apt-get install python-setuptools

And this is the equivalent command on a Fedora Linux system:

.. code-block:: text

   $ sudo yum install python-setuptools

Manual Method
+++++++++++++

To install setuptools by hand under Python 2, first download `ez_setup.py
<http://peak.telecommunity.com/dist/ez_setup.py>`_ then invoke it using the
Python interpreter into which you want to install setuptools.

.. code-block:: text

   $ python ez_setup.py

Once this command is invoked, setuptools should be installed on your
system.  If the command fails due to permission errors, you may need
to be the administrative user on your system to successfully invoke
the script.  To remediate this, you may need to do:

.. code-block:: text

   $ sudo python ez_setup.py

Installing Distribute On Python 3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``setuptools`` doesn't work under Python 3. Instead, you can use
``distribute``, which is a fork of setuptools that does work on Python 3.

Package Manager Method
++++++++++++++++++++++

If you are using a "system" Python it is recommended that you install
the ``distribute`` package from your OS distributor. For example, this works
to do so on an Ubuntu Linux system:

.. code-block:: text

   $ sudo apt-get install python3-setuptools

And this is the equivalent command on a Fedora Linux system:

.. code-block:: text

   $ sudo yum install python3-setuptools

Manual Method
+++++++++++++

To install distribute by hand under Python 3, first download
`distribute_setup.py <http://python-distribute.org/distribute_setup.py>`_
then invoke it using the Python interpreter into which you want to
install setuptools.

.. code-block:: text

   $ python3 distribute_setup.py

Once this command is invoked, distribute should be installed on your system.
If the command fails due to permission errors, you may need to be the
administrative user on your system to successfully invoke the script.  To
remediate this, you may need to do:

.. code-block:: text

   $ sudo python3 distribute_setup.py

.. index::
   pair: install; virtualenv

Installing the ``virtualenv`` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As usual, there are two ways of installing the :term:`virtualenv`
package. You can use the package from your OS distributor or you
can use your recently installed setuptools to install it.

Package Manager Method
++++++++++++++++++++++

In an Ubuntu Linux system this is the command your need to execute:

.. code-block:: text

   $ sudo apt-get install python-virtualenv

And this is the equivalent command on a Fedora Linux system:

.. code-block:: text

   $ sudo yum install python-virtualenv

Setuptools Method
+++++++++++++++++

To install the :term:`virtualenv` package into your setuptools-enabled
Python interpreter with your recently installed setuptools, use
the ``easy_install`` command.

.. warning::

   Python 3.3 includes ``pyvenv`` out of the box, which provides similar
   functionality to ``virtualenv``.  We however suggest using ``virtualenv``
   instead, which works well with Python 3.3.  This isn't a recommendation made
   for technical reasons; it's made because it's not feasible for the authors
   of this guide to explain setup using multiple virtual environment systems.
   We are aiming to not need to make the installation documentation
   Turing-complete.

   If you insist on using ``pyvenv``, you'll need to understand how to install
   software such as ``distribute`` into the virtual environment manually,
   which this guide does not cover.

.. code-block:: text

   $ easy_install virtualenv

This command should succeed, and tell you that the virtualenv package is now
installed.  If it fails due to permission errors, you may need to install it
as your system's administrative user.  For example:

.. code-block:: text

   $ sudo easy_install virtualenv

.. index::
   single: virtualenv
   pair: Python; virtual environment

Creating the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the :term:`virtualenv` package is installed in your Python, you
can then create a virtual environment.  To do so, invoke the
following:

.. code-block:: text

   $ virtualenv --no-site-packages env
   New python executable in env/bin/python
   Installing setuptools.............done.

.. warning::

   Using ``--no-site-packages`` when generating your
   virtualenv is *very important*. This flag provides the necessary
   isolation for running the set of packages required by
   :command:`Yith Library Server`.  If you do not specify
   ``--no-site-packages``, it's possible that
   :command:`Yith Library Server` will not install properly into
   the virtualenv, or, even if it does, may not run properly,
   depending on the packages you've already got installed into your
   Python's "main" site-packages dir.

.. warning:: *do not* use ``sudo`` to run the
   ``virtualenv`` script.  It's perfectly acceptable (and desirable)
   to create a virtualenv as a normal user.

You should perform any following commands that mention a "bin"
directory from within the ``env`` virtualenv dir.

Installing :command:`Yith Library Server` Into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your ``env`` virtualenv installed, you may install
:command:`Yith Library Server` itself using the following commands
from within the virtualenv (``env``) directory you created in the
last step.

.. code-block:: text

   $ cd env
   $ bin/easy_install yith-library-server

The ``easy_install`` command will take longer than the previous ones to
complete, as it downloads and installs a number of dependencies.


Database setup
--------------

:program:`Yith Library Server` uses `MongoDB <http://www.mongodb.org>`_ for
its storage needs. In modern operating systems it is pretty easy to install
MongoDB. As an example, on an Ubuntu Linux system you can use the following
commands

.. code-block:: text

   $ sudo apt-get install mongodb mongodb-server
   $ sudo service mongodb start

Or, in a Fedora Linux system, the equivalent commands are:

.. code-block:: text

   $ sudo yum install mongodb mongodb-server
   $ sudo systemctl start mongod.service

By default :program:`Yith Library Server` will look for a MongoDB server in
``localhost``, listening on port ``27017`` and will use a database
named ``yith-library``. Of couse you can change these settings as explained
in the :ref:`configuration_chapter` section.

Running the server
------------------

In development mode and also for testing purposes you can use the
:command:`pserve` command included in :program:`Yith Library Server`. This will
use the `waitress <http://pypi.python.org/pypi/waitress/>`_ WSGI
server.

.. code-block:: text

   pserve development.ini
     Starting server in PID 6743.
     serving on http://0.0.0.0:6543

Now you can open the `http://0.0.0.0:6543 <http://0.0.0.0:6543>`_ URL in your
browser and start using :program:`Yith Library Server`.

.. warning::
   You should probably want to use a HTTP server and a faster
   WSGI server to run :program:`Yith Library Server` in a real production
   environment.

If you see :program:`Yith Library Server` landing page when opening the previous
link then congratulations! you have succesfully installed the server.
You can now proceed to the :ref:`configuration_chapter` section to
learn about all the options you can use to customize it to your needs.
