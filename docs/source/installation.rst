Installation
============

Yith Library Server is a python 3 application so the first
thing you need to do is install this version of your favourite
language. You will also need the development package since some
of Yith Library Server dependencies need to compile stuff.

.. code-block:: bash

   yum install python3 python3-devel

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
