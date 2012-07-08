Installation
============

Dependencies
------------

Yith Library Server is a python 3 application so the first
thing you need to do is install this version of your favourite
language. You will also need the development package since some
of Yith Library Server dependencies need to compile stuff.

.. code-block:: bash

   sudo yum install python3 python3-devel

Afterwards you should be a good Python citizen and create a
virtualenv so you don't mess your system up:

.. code-block:: bash

   virtualenv -p python3 --no-site-packages yith
   cd yith
   . bin/activate

Now you are ready to download the code and install it in development mode:

.. code-block:: bash

   git clone git@github.com:Yaco-Sistemas/yith-library-server.git
   cd yith-library-server
   python setup.py develop


Database setup
--------------

Yith Library Server uses MongoDB for its storage needs. In modern
operating systems it is pretty easy to install MongoDB. As an example,
in Fedora 17 it is as easy as running these two commands:

.. code-block:: bash

   sudo yum install mongodb mongodb-server
   sudo systemctl start mongod.service

By default Yith Library Server will look for a MongoDB server in `localhost`,
listening on port `27017` and will use a database named `yith-library`.
Of couse you can change these settings by editing the mongo_uri option in
either the `development.ini` or `production.init` configuration files.

Running the server
------------------

In development mode and also for testing purposes you can use the `pserve`
command included in Yith Library Server. This will use the
`waitress <http://pypi.python.org/pypi/waitress/>`_ WSGI server.

.. code-block:: bash

   pserve development.ini
     Starting server in PID 6743.
     serving on http://0.0.0.0:6543

Now you can open the `http://0.0.0.0:6543 <http://0.0.0.0:6543>`_ URL in your
browser and start using Yith Library Server.
