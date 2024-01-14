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

.. note::
    You only need to rez-build/rez-env when you change python file of rezbuild_utils.
    You can just successively call ``build-doc.py`` when only the doc is modified.

**Publish the documentation**

Deploy the documentation to GitHub pages.

You must:

* be on main branch
* have no uncommited changes
* have pushed the branch

.. code-block:: shell

    cd .
    # ensure package is built first (necessary for autodoc)
    rez-build -i
    rez-env sphinx furo rezbuild_utils
    python ./doc/publish-doc.py
