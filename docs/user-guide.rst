.. _user-guide:

User Guide
==========

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

    # Header
    > Content-Type:application/json

    # Querystring parameter
    > page==2

    # Body parameters
    > username=foo
    > full_name='foo bar'

    # Body parameters in raw JSON (new in v0.9.0)
    > number:=1234
    > is_ok:=true
    > names:=["foo","bar"]
    > user:='{"username": "foo", "password": "bar"}'

    # Write them in one line
    > Content-Type:application/json page==2 username=foo

You can also add HTTPie_ options like this:

.. code-block:: bash

    > --form --auth user:pass
    > --verify=no

    # HTTPie options and request parameters in one line
    > --form --auth user:pass username=foo Content-Type:application/json

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

Since v0.6.0, apart from ``httpie`` command, you can also use ``env`` to print
the current session:

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
    > options (new in v0.8.0)

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

    # Remove a header
    > rm -h Content-Type

    # Remove a querystring parameter
    > rm -q apikey

    # Remove a body parameter
    > rm -b username

    # Remove an HTTPie option
    > rm -o --auth

To reset the session, i.e., clear all parameters and options:

.. code-block:: bash

    > rm *

To exit a session, simply enter:

.. code-block:: bash

    > exit


Output Redirection
------------------

*New in v0.6.0.*

You can redirect the output of a command to a file by using the syntax:

.. code-block:: bash

    # Write output to a file
    > COMMAND > /path/to/file

    # Append output to a file
    > COMMAND >> /path/to/file

where ``COMMAND`` can be one of the following:

* ``env``
* ``httpie``
* HTTP actions: ``get``, ``post``, ``put``, ``patch``, ``delete``, ``head``,
  ``options``


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

    # Wipe out the current session and load from a file
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


Pipeline
--------

*New in v0.7.0.*

HTTP Prompt supports simplified pipeline syntax, where you can pipe the output
to a shell command:

.. code-block:: bash

    # Replace 'localhost' to '127.0.0.1'
    > httpie POST http://localhost | sed 's/localhost/127.0.0.1/'
    http http://127.0.0.1

    # Only print the line that contains 'User-Agent' using grep
    > get http://httpbin.org/get | grep 'User-Agent'
        "User-Agent": "HTTPie/0.9.6"

On macOS, you can even copy the result to the clipboard using ``pbcopy``:

.. code-block:: bash

    # Copy the HTTPie command to the clipboard (macOS only)
    > httpie | pbcopy

Another cool trick is to use jq_ to parse JSON data:

.. code-block:: bash

    > get http://httpbin.org/get | jq '.headers."User-Agent"'
    "HTTPie/0.9.6"

**Note**: Syntax with multiple pipes is not supported currently.


Shell Substitution
------------------

*New in v0.7.0.*

Shell substitution happens when you put a shell command between two backticks
like ```...```. This syntax allows you compute a value from the shell
environment and assign the value to a parameter::

    # Set date to current time
    > date==`date -u +"%Y-%m-%d %H:%M:%S"`
    > httpie
    http http://localhost:8000 'date==2016-10-08 09:45:00'

    # Get password from a file. Suppose the file has a content of
    # "secret_api_key".
    > password==`cat ./apikey.txt`
    > httpie
    http http://localhost:8000 apikey==secret_api_key


Configuration
-------------

*New in v0.4.0.*

When launched for the first time, HTTP Prompt creates a user config file at
``$XDG_CONFIG_HOME/http-prompt/config.py`` (or ``%LOCALAPPDATA%/http-prompt/config.py``
on Windows). By default, it's ``~/.config/http-prompt/config.py`` (or
``~/AppData/Local/http-prompt/config.py``).

``config.py`` is a Python module with all the available options you can
customize. Don't worry. You don't need to know Python to edit it. Just open it
up with a text editor and follow the guidance inside.


Persistent Context
------------------

*New in v0.4.0.*

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
replaced by ``env``, ``exec`` and ``source`` commands. See the discussion in
`issue #70 <https://github.com/eliangcs/http-prompt/issues/70>`_ for detail.


``ls``, ``cd``, and OpenAPI/Swagger Specification
-------------------------------------------------

*New in v0.10.0.*

OpenAPI_ (formerly known as Swagger_) is a specifcation that describes an
HTTP/REST API. The ``http-prompt`` has a ``--spec`` option for you to provide
an OpenAPI specification in JSON format. The specification enables HTTP Prompt
to do some cool things like autocomplete API endpoint paths and parameters
for you.

See it in action:

|ls-demo|

To use this feature, specify an OpenAPI/Swagger specification file with
``--spec`` command line option::

    # Specify a spec on local filesystem
    $ http-prompt http://localhost:8000 --spec /path/to/spec.json

    # Specify a spec on the internet (https://apis.guru has lots of them)
    $ http-prompt https://api.github.com --spec https://api.apis.guru/v2/specs/github.com/v3/swagger.json

Then you can use ``ls`` and ``cd`` commands to navigate API endpoints with
autocomplete!


.. |ls-demo| image:: https://asciinema.org/a/107732.png
    :target: https://asciinema.org/a/107732

.. _HTTPie: https://httpie.org
.. _jq: https://stedolan.github.io/jq/
.. _OpenAPI: https://openapis.org
.. _Swagger: http://swagger.io/
