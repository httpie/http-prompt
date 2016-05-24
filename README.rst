HTTP Prompt
===========

|PyPI| |Build| |Coverage| |Workspace|

HTTP Prompt is an interactive command-line HTTP client featuring autocomplete
and syntax highlighting, built on HTTPie_ and prompt_toolkit_.

.. image:: http-prompt.gif


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

Starting a session::

    $ http-prompt http://httpbin.org

To change URL address, use ``cd``::

    > cd api/v1
    > cd http://localhost/api

To add headers, querystring, or body parameters, use the syntax as in HTTPie_.
The following are all valid::

    > Content-Type:application/json username=john
    > 'name=John Doe' apikey==abc
    > Authorization:"Bearer auth_token"

You can also add HTTPie_ options like this::

    > --form --auth user:pass
    > --verify=no username=jane

To preview how HTTP Prompt is going to call HTTPie_, do::

    > httpie post
    http --auth user:pass --form POST http://localhost/api apikey==abc username=john

You can temporarily override the request parameters. The current session won't
be modified::

    > httpie /api/something page==2 --json
    http --json http://localhost/api/something page==2

    > httpie
    http http://localhost

To actually send a request, enter one of the HTTP methods::

    > get
    > post
    > put
    > patch
    > delete
    > head

The above HTTP methods also support temporary overriding::

    > post /api/v1 --form name=jane
    ...

    > httpie
    http http://localhost

To remove an existing header, querystring, body parameter, or HTTPie_ option::

    > rm -h Content-Type
    > rm -q apikey
    > rm -b username
    > rm -o --auth


Roadmap
-------

* User configuration file, i.e., an RC file
* More HTTP headers for autocomplete
* More tests, e.g., integration test and testing on Windows
* More documentation
* Support for advanced HTTPie syntax, e.g, ``field:=json`` and ``field=@file.json``
* Inline shell command evaluation
* HTTP/2 support


.. |PyPI| image:: https://img.shields.io/pypi/v/http-prompt.svg
    :target: https://pypi.python.org/pypi/http-prompt

.. |Build| image:: https://api.travis-ci.org/eliangcs/http-prompt.svg?branch=master
    :target: https://travis-ci.org/eliangcs/http-prompt

.. |Coverage| image:: https://coveralls.io/repos/github/eliangcs/http-prompt/badge.svg?branch=master
    :target: https://coveralls.io/github/eliangcs/http-prompt?branch=master

.. |Workspace| image:: http://beta.codenvy.com/factory/resources/codenvy-contribute.svg
    :target: http://beta.codenvy.com/f?id=bjzn6mwwz8x8xr4q

.. _HTTPie: https://github.com/jkbrzt/httpie
.. _prompt_toolkit: https://github.com/jonathanslenders/python-prompt-toolkit
