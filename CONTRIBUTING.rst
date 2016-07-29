Contributing
============

Any contributions are welcome and greatly appreciated!


Bugs, Feature Requests, or Questions?
-------------------------------------

https://github.com/eliangcs/http-prompt/issues


Developer Guide
---------------

This guide is for developers who want to contribute code to this project. This
project follows the common conventions of a Python/GitHub project. So if you're
already an experienced Python/GitHub user, it should be straightforward for you
to set up your development environment and send patches. Generally, the steps
include:

1. Fork and clone the repo
2. Create a virtualenv for this project
3. Install dependent packages with ``pip install -e .``
4. Install test dependent packages with ``pip install -r requirements-test.txt``
5. Make your changes to the code
6. Run tests with ``py.test`` and ``tox``
7. Commit and push your changes
8. Send a pull request
9. Wait to be reviewed and get merged!

If you're not familiar with any of the above steps, read the following
instructions.


Forking
~~~~~~~

*Fork* is a term invented by GitHub. It means copy someone else's project to
your account, so you can make changes without interfering with the original
project.

To fork HTTP Prompt, just click the **Fork** button on HTTP Prompt's GitHub
project page. Then you clone your fork to your local computer::

    $ cd ~/Projects
    $ git clone git@github.com:{YOUR_USERNAME}/http-prompt.git

Read `Forking Projects`_ on GitHub to learn more.


Working with virtualenv
~~~~~~~~~~~~~~~~~~~~~~~

*virtualenv* is the de facto standard tool when developing a Python project.
Instead of pollute your system-wide Python installation with different Python
projects, virtualenv creates an isolated Python environment exclusively for a
Python project.

There are several tools you can use for managing virtualenvs. In this guide,
I'll show you how to use pyenv_ and pyenv-virtualenv_, which I use personally.

Make sure you have installed pyenv_ and pyenv-virtualenv_ first.

HTTP Prompt should work on Python 2.6, 2.7, 3.3, 3.4, and 3.5. You can use any
of these Python versions as your development environment, but using the latest
version (3.5.x) is probably the best. You can install the latest Python with
pyenv::

    $ pyenv install 3.5.1

This will install Python 3.5.1 in ``~/.pyenv/versions/3.5.1`` directory. To
create a virtualenv for HTTP Prompt, do::

    $ pyenv virtualenv 3.5.1 http-prompt

The command means: create a virtualenv named "http-prompt" from based on Python
3.5.1. The virtualenv can be found at ``~/.pyenv/versions/3.5.1/envs/http-prompt``.

To activate the virtualenv, do::

    $ pyenv activate http-prompt

This will switch your Python environment from the system-wide Python to the
virtualenv (named "http-prompt") Python.

To go back to the system-wide Python, you have to deactivate the virtualenv::

    $ pyenv deactivate http-prompt

Refer to pyenv_ and pyenv-virtualenv_ if anything else is unclear.


Installing Dependent Packages
-----------------------------

Make sure you activated your virtualenv first. It is also recommended to use
the latest version of pip. You can upgrade it with::

    $ pip install -U pip

Install HTTP Prompt with its dependent packages::

    $ cd ~/Projects/http-prompt
    $ pip install -e .

``pip install -e .`` means install the package in editable mode (or developer
mode). This allows you to edit code directly in ``~/Projects/http-prompt``
without reinstalling the package.  Without the ``-e`` option, the package will
be installed to Python's ``site-packages`` directory, which is not convenient
for developing.


Installing Test Dependent Packages
----------------------------------

Test tools are placed in a separate file named ``requirements-test.txt``. To
install them, do::

    $ cd ~/Projects/http-prompt
    $ pip install -r requirements-test.txt


Making Your Changes
-------------------

Code Style
~~~~~~~~~~

Always lint your code with Flake8_. You can set it up in your code editor or
simply use `flake8` in the command line.

`The Hitchhiker’s Guide to Python`_ provides the best Python coding practices.
I recommend anyone who wants to write good Python code to read it.

Adding Features
~~~~~~~~~~~~~~~

Before you add a new feature, make sure you create an issue making a proposal
first, because you don't want to waste your time on something that I don't
agree upon.

Python 2 and 3 Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HTTP Prompt is compatible with Python 2 and 3. When you code, keep in mind that
you're coding for Python 2 and 3. You can use Tox_ (see below) to make sure the
code is runnable on both Python 2 and 3.


Running Tests
-------------

Single Python Version
~~~~~~~~~~~~~~~~~~~~~

Make sure your virtualenv is activated. To run tests, do::

    $ cd ~/Projects/http-prompt
    $ py.test

``py.test`` runs the tests with your virtualenv's Python version. This is good
for fast testing. To test the code against multiple Python versions, you use
Tox_.

Multiple Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you're **not** in a virtualenv and you have installed all the Python
versions we're targeting. If not, do::

    $ pyenv install 2.6.9
    $ pyenv install 2.7.11
    $ pyenv install 3.3.6
    $ pyenv install 3.4.4
    $ pyenv install 3.5.1
    $ pyenv install pypy-5.0.0
    $ pyenv install pypy3-2.4.0

To use Tox_ with pyenv_, you have to instruct pyenv to use multiple Python
versions for the project::

    $ cd ~/Projects/http-prompt
    $ pyenv local 3.5.1 3.4.4 3.3.6 2.7.11 2.6.9 pypy-5.0.0 pypy3-2.4.0

This will generate a ``.python-version`` in the project directory::

    $ cat ~/Projects/http-prompt/.python-version
    3.5.1
    3.4.4
    3.3.6
    2.7.11
    2.6.9
    pypy-5.0.0
    pypy3-2.4.0

Again, make sure you're **not** in a virtualenv, run ``tox``::

    $ cd ~/Projects/http-prompt
    $ tox

Tox_ will install the test Python environments in the ``.tox/`` directory in
the project directory, and run the test code against all the Python versions
listed above.


Code Review
-----------

Once you made changes and the tests pass, push your modified code to your
GitHub account. Submit a pull request (PR) on GitHub for me to review. If the
patch is good, I'll merge it to the master branch and ship the new code in the
next release. If the patch needs improvements, I'll give you feedback so you
can modify accordingly and resubmit to the PR.


.. _Flake8: http://flake8.pycqa.org/en/latest/index.html
.. _Forking Projects: https://guides.github.com/activities/forking/
.. _pyenv-virtualenv: https://github.com/yyuu/pyenv-virtualenv
.. _pyenv: https://github.com/yyuu/pyenv
.. _The Hitchhiker’s Guide to Python: http://docs.python-guide.org/en/latest/
.. _Tox: https://tox.readthedocs.io/en/latest/
