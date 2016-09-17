HTTP Prompt
===========

|PyPI| |Travis| |Appveyor| |Coverage|

HTTP Prompt is an interactive command-line HTTP client featuring autocomplete
and syntax highlighting, built on HTTPie_ and prompt_toolkit_.

.. image:: https://raw.githubusercontent.com/eliangcs/http-prompt/master/http-prompt.gif


Installation
------------

Just install it like a regular Python package::

    $ pip install http-prompt

You'll probably see some permission errors if you're trying to install it on
the system-wide Python. It isn't recommended. But if that's what you want to
do, you need to ``sudo``::

    $ sudo pip install http-prompt

Another alternative is to use ``--user`` option to install the package into
your user directory::

    $ pip install --user http-prompt

To upgrade HTTP Prompt, do::

    $ pip install -U http-prompt


Quickstart
----------

To start a session, you use the ``http-prompt`` executable:

.. code-block:: bash

    # Start with the last session or http://localhost:8000
    $ http-prompt

    # Start with the given URL
    $ http-prompt http://httpbin.org

    # Start with some initial options
    $ http-prompt localhost:8000/api --auth user:pass username=somebody

Once you're in a session, you can use the following commands.

To change URL address, use ``cd``:

.. code-block:: bash

    # Relative URL path
    > cd api/v1

    # Absolute URL
    > cd http://localhost/api

To add headers, querystring, or body parameters, use the syntax as in HTTPie_.
The following are all valid:

.. code-block:: bash

    > Content-Type:application/json username=john
    > 'name=John Doe' apikey==abc
    > Authorization:"Bearer auth_token"

You can also add HTTPie_ options like this:

.. code-block:: bash

    > --form --auth user:pass
    > --verify=no username=jane

To preview how HTTP Prompt is going to call HTTPie_, do:

.. code-block:: bash

    > httpie post
    http --auth user:pass --form POST http://localhost/api apikey==abc username=john

You can temporarily override the request parameters by supplying options and
parameters in ``httpie`` command. The overrides won't affect the later
requests.

.. code-block:: bash

    # No parameters initially
    > httpie
    http http://localhost

    # Override parameters temporarily
    > httpie /api/something page==2 --json
    http --json http://localhost/api/something page==2

    # Current state is not affected by the above overrides
    > httpie
    http http://localhost

Besides ``httpie`` command, you can also use ``env`` to print the current
session:

.. code-block:: bash

    > env
    --verify=no
    cd http://localhost
    page==10
    limit==20

To actually send an HTTP request, enter one of the HTTP methods:

.. code-block:: bash

    > get
    > post
    > put
    > patch
    > delete
    > head

The above HTTP methods also support temporary overriding:

.. code-block:: bash

    # No parameters initially
    > httpie
    http http://localhost

    # Send a request with some overrided parameters
    > post /api/v1 --form name=jane

    # Current state remains intact
    > httpie
    http http://localhost

To remove an existing header, a querystring parameter, a body parameter, or an
HTTPie_ option:

.. code-block:: bash

    > rm -h Content-Type
    > rm -q apikey
    > rm -b username
    > rm -o --auth

To reset the session, i.e., clear all parameters and options:

.. code-block:: bash

    > rm *

To exit a session, simply enter:

.. code-block:: bash

    > exit


Output Redirection
------------------

You can redirect the output of a command to a file by using the syntax:

.. code-block:: bash

    # Write output to a file
    > COMMAND > /path/to/file

    # Append output to a file
    > COMMAND >> /path/to/file

where ``COMMAND`` can be one of the following:

* ``env``
* ``httpie``
* HTTP actions: ``get``, ``post``, ``put``, ``patch``, ``delete``, ``head``


Saving and Loading Sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of the use cases of output redirection is to save and load sessions, which
is especially useful for team collaboration, where you want to share your
sessions with your team members.

To save your current session, you redirect the output of ``env`` to a file:

.. code-block:: bash

    > env > /path/to/file

To load a saved session, you can use ``source`` or ``exec``. Their only
difference is that ``exec`` wipes out the current session before loading.
Usage:

.. code-block:: bash

    # Update the current session
    > source /path/to/file

    # Overwrite the current session completely
    > exec /path/to/file


Saving HTTP Respones
~~~~~~~~~~~~~~~~~~~~

Printing HTTP responses to the console is good for small text responses. For
larger text or binary data, you may want to save the response to a file. Usage:

.. code-block:: bash

    # Save http://httpbin.org/image/png to a file
    > cd http://httpbin.org/image/png
    > get > pig.png

    # Or use this one-liner
    > get http://httpbin.org/image/png > pig.png


Configuration
-------------

When launched for the first time, HTTP Prompt creates a user config file at
``$XDG_CONFIG_HOME/http-prompt/config.py`` (or ``%LOCALAPPDATA%/http-prompt/config.py``
on Windows). By default, it's ``~/.config/http-prompt/config.py`` (or
``~/AppData/Local/http-prompt/config.py``).

``config.py`` is a Python module with all the available options you can
customize. Don't worry. You don't need to know Python to edit it. Just open it
up with a text editor and follow the guidance inside.


Persistent Context
------------------

HTTP Prompt keeps a data structure called *context* to represent your current
session. Every time you enter a command modifying your context, HTTP Prompt
saves the context to your filesystem, enabling you to resume your previous
session when you restart ``http-prompt``.

The last saved context is located at ``$XDG_DATA_HOME/http-prompt/context.hp``
(or ``%LOCALAPPDATA%/http-prompt/context.hp`` on Windows). By default, it's
``~/.local/share/http-prompt/context.hp`` (or ``~/AppData/Local/http-prompt/context.hp``).

As context data may contain sensitive data like API keys, you should keep the
user data directory private. By default, HTTP Prompt sets the modes of
``$XDG_DATA_HOME/http-prompt`` to ``rwx------`` (i.e., ``700``) so that the
only person who can read it is the owner (you).

**Note for users of older versions**: Since 0.6.0, HTTP Prompt only stores the
last context instead of grouping multiple contexts by hostnames and ports like
it did previously. We changed the behavior because the feature can be simply
replaced by ``source`` and ``env`` commands. See the discussion in
`issue #70 <https://github.com/eliangcs/http-prompt/issues/70>`_ for detail.


Roadmap
-------

* Support for advanced HTTPie syntax, e.g, ``field:=json`` and ``field=@file.json``
* Shell command evaluation
* Support for cURL command and raw format preview
* Improve autocomplete
* Python syntax evaluation
* HTTP/2 support


Contributing
------------

See CONTRIBUTING.rst_.


Thanks
------

* HTTPie_: for designing such a user-friendly HTTP CLI
* prompt_toolkit_: for simplifying the work of building an interactive CLI
* Parsimonious_: for the PEG parser used by this project
* pgcli_: for the inspiration of this project
* Contributors_: for improving this project


.. |PyPI| image:: https://img.shields.io/pypi/v/http-prompt.svg
    :target: https://pypi.python.org/pypi/http-prompt

.. |Travis| image:: https://api.travis-ci.org/eliangcs/http-prompt.svg?branch=master
    :target: https://travis-ci.org/eliangcs/http-prompt

.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/9tyrtce5omcq1yyk/branch/master?svg=true
    :target: https://ci.appveyor.com/project/eliangcs/http-prompt/branch/master

.. |Coverage| image:: https://coveralls.io/repos/github/eliangcs/http-prompt/badge.svg?branch=master
    :target: https://coveralls.io/github/eliangcs/http-prompt?branch=master

.. _CONTRIBUTING.rst: https://github.com/eliangcs/http-prompt/blob/master/CONTRIBUTING.rst
.. _Contributors: https://github.com/eliangcs/http-prompt/graphs/contributors
.. _HTTPie: https://github.com/jkbrzt/httpie
.. _Parsimonious: https://github.com/erikrose/parsimonious
.. _pgcli: https://github.com/dbcli/pgcli
.. _prompt_toolkit: https://github.com/jonathanslenders/python-prompt-toolkit
