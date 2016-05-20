HTTP Prompt
===========

|PyPI| |Build| |Coverage|

HTTP Prompt is an interactive command-line HTTP client featuring autocomplete
and syntax highlighting, built on HTTPie_ and prompt_toolkit_.

.. image:: http-prompt.gif


Installation
------------

Just install it like a regular Python package::

    $ pip install http-prompt

You'll probably see some permission errors if you're installing it on the
system-wide Python. If that's what you want to do, you need to ``sudo``::

    $ sudo pip install http-prompt

To upgrade HTTP Prompt, do::

    $ pip install -U http-prompt


Quickstart
----------

Starting a session::

    $ http-prompt http://httpbin.org

To change URL address, use ``cd``::

    > cd api/v1
    > cd http://localhost/api

To add headers, querystring, or body parameters, use the syntax as in HTTPie_::

    > Content-Type:application/json username=john
    > 'name=John Doe' apikey=abc

You can also add HTTPie_ options like this::

    > --form --auth user:pass

To preview how HTTP Prompt is going to call HTTPie_, do::

    > httpie post
    http --auth user:pass --form POST http://localhost/api apikey==abc username=john

To actually send a request, enter one of the HTTP methods::

    > get
    > head
    > post
    > put
    > patch
    > delete

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
* Support for advanced HTTPie syntax, e.g, `field:=json` and `field=@file.json`
* Inline shell command evaluation
* HTTP/2 support


.. |PyPI| image:: https://img.shields.io/pypi/v/http-prompt.svg
    :target: https://pypi.python.org/pypi/http-prompt

.. |Build| image:: https://api.travis-ci.org/eliangcs/http-prompt.svg?branch=master
    :target: https://travis-ci.org/eliangcs/http-prompt

.. |Coverage| image:: https://coveralls.io/repos/github/eliangcs/http-prompt/badge.svg?branch=master
    :target: https://coveralls.io/github/eliangcs/http-prompt?branch=master

.. _HTTPie: https://github.com/jkbrzt/httpie
.. _prompt_toolkit: https://github.com/jonathanslenders/python-prompt-toolkit
