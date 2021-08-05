.. _contributor-guide:

Contributor Guide
=================

This document is for developers who want to contribute code to this project.
Any contributions are welcome and greatly appreciated!

This project follows the common conventions of a Python/GitHub project. So if
you're already an experienced Python/GitHub user, it should be straightforward
for you to set up your development environment and send patches. Generally, the
steps include:

1. Fork and clone the repo
2. Create a virtualenv for this project
3. Install dependent packages with ``pip install -e .``
4. Install test dependent packages with ``pip install -r requirements-test.txt``
5. Make your changes to the code
6. Run tests with ``pytest`` and ``tox``
7. Commit and push your changes
8. Send a pull request
9. Wait to be reviewed and get merged!

If you're not familiar with any of the above steps, read the following
instructions.


Forking
-------

Fork_ is like copying someone else's project to your account, so you can start
your own independent development without interfering with the original one.

To fork HTTP Prompt, just click the **Fork** button on HTTP Prompt's GitHub
project page. Then you clone your fork to your local computer::

    $ cd ~/Projects
    $ git clone git@github.com:{YOUR_USERNAME}/http-prompt.git

Read `Forking Projects`_ on GitHub to learn more.


Working with virtualenv
-----------------------

*virtualenv* is the de facto standard tool when developing a Python project.
Instead of polluting your system-wide Python installation with different Python
projects, virtualenv creates an isolated Python environment exclusively for a
Python project.

There are several tools you can use for managing virtualenvs. In this guide,
we'll show you how to use pyenv_ and pyenv-virtualenv_, which is one of the
most popular virtualenv management tools.

Make sure you have installed pyenv_ and pyenv-virtualenv_ first.

HTTP Prompt should work on Python 2.6, 2.7, 3.3 to 3.6. You can use any
of these Python versions as your development environment, but using the latest
version (3.6.x) is probably the best. You can install the latest Python with
pyenv::

    $ pyenv install 3.6.0

This will install Python 3.6.0 in ``~/.pyenv/versions/3.6.0`` directory. To
create a virtualenv for HTTP Prompt, do::

    $ pyenv virtualenv 3.6.0 http-prompt

The command means: create a virtualenv named "http-prompt" based on Python
3.6.0. The virtualenv can be found at ``~/.pyenv/versions/3.6.0/envs/http-prompt``.

To activate the virtualenv, do::

    $ pyenv activate http-prompt

This will switch your Python environment from the system-wide Python to the
virtualenv's (named "http-prompt") Python.

To go back to the system-wide Python, you have to deactivate the virtualenv::

    $ pyenv deactivate

Refer to pyenv_ and pyenv-virtualenv_ if anything else is unclear.


Installing Dependent Packages
-----------------------------

The dependent packages should be installed on a virtualenv, so make sure you
activate your virtualenv first. If not, do::

    $ pyenv activate http-prompt

It is also recommended to use the latest version of pip. You can upgrade it
with::

    $ pip install -U pip

Install HTTP Prompt with its dependent packages::

    $ cd ~/Projects/http-prompt
    $ pip install -e .

``pip install -e .`` means install the ``http-prompt`` package in editable mode
(or developer mode). This allows you to edit code directly in
``~/Projects/http-prompt`` without reinstalling the package. Without the ``-e``
option, the package will be installed to Python's ``site-packages`` directory,
which is not convenient for developing.


Installing Test Dependent Packages
----------------------------------

Test requirements are placed in a separate file named ``requirements-test.txt``.
To install them, do::

    $ cd ~/Projects/http-prompt
    $ pip install -r requirements-test.txt


Making Your Changes
-------------------

Code Style
~~~~~~~~~~

Always lint your code with Flake8_. You can set it up in your code editor or
simply use ``flake8`` in the command line.

`The Hitchhiker’s Guide to Python`_ provides the best Python coding practices.
We recommend anyone who wants to write good Python code to read it.

Adding Features
~~~~~~~~~~~~~~~

Before you add a new feature, make sure you create an issue making a proposal
first, because you don't want to waste your time on something that the
community don't agree upon.

Python Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HTTP Prompt is compatible with Python 3.6+.

Documentation
~~~~~~~~~~~~~

Documentation is written in Sphinx_. To build documentation, you need to
install Sphinx_ first::

    $ pip install sphinx

To build and view documentation in HTML, do::

    $ cd ~/Projects/http-prompt/docs
    $ make html
    $ open _build/html/index.html


Running Tests
-------------

Single Python Version
~~~~~~~~~~~~~~~~~~~~~

Make sure your virtualenv is activated. To run tests, do::

    $ cd ~/Projects/http-prompt
    $ pytest

``pytest`` runs the tests with your virtualenv's Python version. This is good
for fast testing. To test the code against multiple Python versions, you use
Tox_.

Multiple Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~

All the commands in this section should **NOT** be run in a virtualenv.
Deactivate it first if you're in a virtualenv::

    $ pyenv deactivate

Make sure you have installed all the Python versions we're targeting. If not,
do::

    $ pyenv install 3.6.0
    $ pyenv install 3.7.0
    $ pyenv install 3.8.0

To use Tox_ with pyenv_, you have to instruct pyenv to use multiple Python
versions for the project::

    $ cd ~/Projects/http-prompt
    $ pyenv local 3.6.0 3.7.0 3.8.0

This will generate a ``.python-version`` in the project directory::

    $ cat ~/Projects/http-prompt/.python-version
    3.6.0
    3.7.0
    3.8.0

This tells pyenv_ to choose a Python version based on the above order. In this
case, 3.6.0 is the first choice, so any Python executables (such as ``python``
and ``pip``) will be automatically mapped to the ones in
``~/.pyenv/versions/3.8.0/bin``.

We want to run ``tox`` using on Python 3.8.0. Make sure you have installed
Tox_::

    $ pip install tox

To run tests, execute ``tox``::

    $ cd ~/Projects/http-prompt
    $ tox

Tox_ will install the test Python environments in the ``.tox/`` directory in
the project directory, and run the test code against all the Python versions
listed above.


Code Review
-----------

Once you made changes and all the tests pass, push your modified code to your
GitHub account. Submit a pull request (PR) on GitHub for the maintainers to
review. If the patch is good, The maintainers will merge it to the master
branch and ship the new code in the next release. If the patch needs
improvements, we'll give you feedback so you can modify accordingly and
resubmit it to the PR.


.. _Flake8: http://flake8.pycqa.org/en/latest/index.html
.. _Fork: https://en.wikipedia.org/wiki/Fork_(software_development)
.. _Forking Projects: https://guides.github.com/activities/forking/
.. _pyenv-virtualenv: https://github.com/yyuu/pyenv-virtualenv
.. _pyenv: https://github.com/yyuu/pyenv
.. _Sphinx: http://www.sphinx-doc.org/
.. _The Hitchhiker’s Guide to Python: http://docs.python-guide.org/en/latest/
.. _Tox: https://tox.readthedocs.io/en/latest/
