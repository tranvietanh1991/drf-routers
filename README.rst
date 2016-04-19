drf-routers
======================================

|build-status-image| |pypi-version|

Overview
--------

Nested resources for the Django Rest Framework

Requirements
------------

-  Python (2.7)
-  Django (1.7, 1.8)
-  Django REST Framework (3.0, 3.1, 3.2, 3.3)

Installation
------------

Install using ``pip``\ …

.. code:: bash

    $ pip install drf-routers

Example
-------

TODO: Write example.

Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with runtests.

.. code:: bash

    $ ./runtests.py

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

Documentation
-------------

To build the documentation, you’ll need to install ``mkdocs``.

.. code:: bash

    $ pip install mkdocs

To preview the documentation:

.. code:: bash

    $ mkdocs serve
    Running at: http://127.0.0.1:8000/

To build the documentation:

.. code:: bash

    $ mkdocs build

.. _tox: http://tox.readthedocs.org/en/latest/
