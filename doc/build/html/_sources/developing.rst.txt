Developing
==========

Documentation for maintaining the repository.

tests
-----

**Running tests**

.. code-block:: shell

    cd .
    # ensure package is build first
    rez-build -i

    rez-test rezbuild_utils

**Running a specific tests**

.. code-block:: shell

    # only run the tests for python 3.9 defined in the package.py
    rez-test rezbuild_utils unit-39

documentation
-------------

**Build the documentation**

.. code-block:: shell

    cd .
    # ensure package is built first (necessary for autodoc)
    rez-build -i
    rez env sphinx furo rezbuild_utils
    python ./doc/build-doc.py -a

The documentation can then be found in ``./doc/build/html/index.html``